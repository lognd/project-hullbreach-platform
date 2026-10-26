# hullbreach_server

The platform API for Project Hullbreach. It owns everything that is not
time-critical: accounts and token sessions, ELO, match history and stats,
the item catalog and cosmetic store, and admin moderation. The game server
reports match results here over REST; the web frontend and the game client
both authenticate against it. Real-time match traffic never touches it.

New here? Start at [picking-up-work.md](picking-up-work.md). The Jira
cross-reference for every ticket in this repo lives in
[backlog.md](backlog.md).

## Public API

`main` parses CLI flags, loads `.env`, builds an `AppConfig`
(pyproject.toml, then `HULLBREACH_*` env vars, then CLI flags), and hands it
to `App`, which runs uvicorn. `AppConfig.from_external` returns a typani
`Result[AppConfig, ConfigError]`: an unreadable or malformed config file, an
unknown key (a typo such as `databse_url`) or an invalid value is an `Err`
whose message names the key and never the value (so a database URL password
cannot leak); `main` prints it and exits 1. The config file is the explicit
argument, else `$HULLBREACH_CONFIG`, else the nearest `pyproject.toml` above
the cwd that has a `[tool.hullbreach_server]` table, and the one used is
logged at INFO. `database_url` is required and has no default (INV-005).
`cors_origins` must be explicit `http(s)` origins (no `*`, path or query;
whitespace and empty entries in the env list are dropped), and `create_app`
allows credentials only with those origins and only the `GET`/`POST`/`OPTIONS`
methods and `Authorization`/`Content-Type` headers the API uses (INV-004). Running with no subcommand still serves; a
`db` subcommand group (`db upgrade`, `db seed`) instead runs the given
database maintenance step and exits without building `App`/`create_app`.
Before serving, `App.__call__` fails fast: it validates the auth
environment variables, initialises the process-wide engine from
`AppConfig.database_url` (`db.init_engine`) and runs `check_connectivity`
on that same engine, exiting non-zero and logging the error at `ERROR`
instead of calling `uvicorn.run` against a database it cannot reach, so the
database checked is the database served. `create_app`'s lifespan
initialises the same engine (idempotently) and disposes it on shutdown.
`create_app` is the pure, socket-free core that
tests exercise through `TestClient`. Routes live in `api/`, one module per
resource, each exposing a `router` that `api_router` mounts under `/api/v1`;
`health` is the liveness probe, which never touches the database; `ready`
is the readiness probe, returning 200 with `{"status": "ready", "database":
"ok"}` when `check_connectivity` succeeds against the request's database
session, or 503 (`NotReadyResponse`, declared in the OpenAPI schema) with
`{"status": "not_ready", "database": "unreachable"}` otherwise. The `logging` subpackage provides
`get_logger`, wired per the house logging convention (stdout for DEBUG/INFO,
stderr for WARNING+). `SimpleFormatter` appends tracebacks and
`stack_info` like the stdlib formatter; `BelowLevelFilter` raises
`ValueError` for an unknown level name; `get_logger` loads
`logging/config.toml` once (lock-guarded) and a missing or invalid file
raises from every importing module, by design.

The `db` package is the SQLAlchemy 2.x surface: `create_db_engine(url)`
builds an `Engine` (normalizing a bare `postgresql://` URL to the
`psycopg` v3 driver), `check_connectivity(engine)` runs `SELECT 1` and
returns a typani `Result[None, DatabaseError]` whose message names the
host/port/database but never a raw URL or password, and `Base` is the
shared `DeclarativeBase` (with the ix/uq/ck/fk/pk naming convention) that
every ORM model and the Alembic env import. `init_engine(url)` builds the
process-wide engine and sessionmaker once, under a lock, from the caller's
`AppConfig.database_url` (repeat calls with the same URL return the same
engine; a different URL raises until `dispose_engine()` closes the pool and
resets the state). `get_engine`/`get_sessionmaker` return that engine and
raise `RuntimeError` if it was never initialised -- the `db` package no
longer re-reads configuration itself. `get_db` is the FastAPI dependency
that yields a session per request and closes it afterward.

`src/hullbreach_server/db/models/user.py` holds the first ORM model:
`User` (table `users`) -- `id` (UUID), unique `username`/`email`,
`password_hash`, a `role` (`Role.player` default, stored as a `VARCHAR`
with a real `ck_users_role` CHECK constraint via `native_enum=False` rather
than a Postgres native enum), and `created_at`.
`src/hullbreach_server/auth/passwords.py` provides `hash_password`/
`verify_password`, Argon2id via `pwdlib.PasswordHash.recommended()`.
`verify_password` never raises for bad stored data: an unrecognised or
corrupt hash is logged at ERROR and answers `False`, so login returns an
ordinary 401. `verify_against_dummy_hash` burns one full Argon2 verify
against a throwaway hash and returns `False`; login calls it for an
unknown username so response time is not an account-existence oracle
(INV-001). `logging.sanitize_for_log(value)` returns a length-capped
`repr`, the only way unauthenticated input (e.g. a login username) may
reach a log line (INV-003).

### Auth sessions

`src/hullbreach_server/db/models/session.py` holds `Session` (table
`sessions`) -- `id` (UUID), `user_id` (FK to `users.id`, `ON DELETE
CASCADE`, indexed), a unique `token_hash` (sha256 of the bearer token,
hex-encoded; the plaintext token is never stored), `created_at`,
`expires_at`, and a nullable `revoked_at`. A session is valid iff
`revoked_at is None and expires_at > now()`. Those two timestamp columns
use the shared `db/models/types.py::UTCDateTime` type decorator (also used
by `User.created_at`, so every timestamp is tz-aware on SQLite and Postgres), whose
`process_result_value` re-attaches UTC tzinfo to a value SQLite returns
naive, so expiry/revocation comparisons never mix naive and aware
datetimes regardless of the backing database.
`src/hullbreach_server/auth/sessions.py` provides `issue_session(db,
user)` (creates a `Session`, returns the row plus the one-time plaintext
token, `secrets.token_urlsafe(32)`; expiry is
`HULLBREACH_SESSION_TTL_SECONDS` seconds from issuance, default 14 days),
`resolve_session(db, token)` (returns a typani `Result[Session,
SessionError]`, `Err` on an unknown, expired, or revoked token),
`revoke_session(db, session)` (sets `revoked_at`), and
`revoke_all_sessions(db, user)` (revokes every non-revoked session for
that user), and `revoke_other_sessions(db, user, keep)` (the same, sparing
the session `keep`; used on a password change, T-0034).
`src/hullbreach_server/auth/deps.py` provides the FastAPI dependency
`get_current_user`, which resolves the `Authorization: Bearer <token>`
header via `resolve_session` and returns an `AuthContext(user, session)`,
raising 401 uniformly for a missing header, an unknown token, an expired
session, or a revoked session (never FastAPI's default 403 on a missing
credential). Both are plain `def` dependencies so FastAPI runs them in the
threadpool next to the sync `get_db` session, not on the event loop.
`require_admin` composes `get_current_user`: it raises 403
`{"detail": "admin role required"}` if the resolved caller's role is
not `Role.admin`, and otherwise returns the same `AuthContext`. 401
means "I don't know who you are"; 403 means "I know who you are and the
answer is no" -- a Player token is fully authenticated, merely
unauthorized, so `require_admin` never returns 401. No production admin
route exists yet in milestone 0.1.0 (admin moderation is a later
milestone); `require_admin` is exercised by a test-only router mounted
directly on the test app fixture (`tests/unit/test_roles.py`).

### Auth API

`POST /api/v1/auth/register` (`src/hullbreach_server/api/auth.py::register`)
takes a `RegisterRequest` (`username` 3-32 chars of `[A-Za-z0-9_.-]`,
`email` as `EmailStr` of at most 254 chars (lower-cased on input),
`password` 8-128 chars; every bound is a 422 before any hashing, INV-002;
`role` is deliberately not a field at all, never merely ignored) and returns a `UserProfile` (`id`, `username`,
`email`, `role`, `currency`, `rating`, `created_at`) with 201 on success.
`UserProfile.from_user(user, rating)` builds the response from the persisted
`User` row and the caller-supplied `rating`, which register, login, `GET
/me` and `PATCH /me` read from `services/matches.py::current_rating` (1200
until the player has a rated match); `currency` is `0` (not a real column
yet). A pre-query (`_duplicate_field`, case-insensitive) checks for
an existing `username` or `email` before the insert, so a 409 response
can name the specific offending field (`{"detail": "username already
taken", "field": "username"}` or the `email` equivalent). The database's
`lower()` unique indexes stay authoritative: a concurrent registration
that loses the insert race hits `IntegrityError`, which is rolled back
and mapped to the same 409. The 401/409/429/503 bodies are declared on
the route decorators (`ErrorDetail`, `ConflictResponse`,
`NotReadyResponse`), so `/api/openapi.json` describes the failure
contract. A too-short password or malformed email fails
pydantic validation with FastAPI's default 422, no custom body needed.

`POST /api/v1/auth/login` (`src/hullbreach_server/api/auth.py::login`)
takes a `LoginRequest` (`username` 1-32 chars, `password` at most 128
chars, no `min_length`; both bounded, INV-002) and, on valid credentials, returns a
`LoginResponse` (`token`, `user: UserProfile`) with 200 -- the token
comes from `auth/sessions.py::issue_session` (T-0019). An unknown
username and a wrong password both get the identical 401
`{"detail": "invalid username or password"}`, and both run exactly one
Argon2 verify (the unknown-user path against a dummy hash), so neither
the body nor the response time confirms account existence (INV-001).
Username lookup is case-insensitive. A failed-login rate limiter guards
every attempt: `reserve_login_attempt` atomically checks the limit and
records the attempt under one lock; `clear_failed_logins` (on success)
undoes it. State is an in-process `dict[str, deque[datetime]]` keyed by
lower-cased username (`HULLBREACH_LOGIN_RATE_LIMIT_MAX`/
`_WINDOW_SECONDS`, default 5 attempts / 60 seconds). A key exists only
while it holds in-window attempts and at most 10,000 usernames are
tracked (expired keys are swept first, then the oldest is evicted), so
spraying unique usernames cannot grow memory (INV-002). Over the limit
the route answers 429 with a `Retry-After` header (seconds until the
oldest attempt leaves the window). The store is explicitly
single-instance for 0.1.0 -- it does not survive a process restart or
work across multiple API instances. `current_time()` is the limiter's
one clock read per request. The username in log lines always goes
through `sanitize_for_log` (INV-003). `HULLBREACH_SESSION_TTL_SECONDS`
and the two rate-limit variables must be positive integers:
`validate_auth_env()` returns an `Err(AuthEnvError)` naming the bad
variable (the server checks it at startup and exits non-zero), and the
request-time readers fall back to the default with an ERROR log instead
of raising a 500.

Login also sets the web session cookie (`auth/cookies.py::set_session_cookie`,
~6TZCHZ0): `hullbreach_session` carries the same token, `HttpOnly`,
`SameSite=Lax`, `Path=/api`, `Max-Age` equal to the session's remaining
life, and `Secure` unless every `HULLBREACH_CORS_ORIGINS` entry is plain-http
loopback (`cookie_secure`), so local `make demo` works over http while any
deployed origin gets `Secure`. The JSON `token` is unchanged, so the game
client's bearer flow is untouched. `get_current_user`/`get_optional_user`
take the bearer header first and fall back to the cookie
(`auth/cookies.py::extract_token`, a typani `Result`). CSRF: a request
authenticated by cookie alone must carry the `X-Hullbreach-Web` header on any
method other than GET/HEAD/OPTIONS or it is refused 403 (a cross-site form
cannot set a custom header, and a cross-site `fetch` needs a CORS preflight
that INV-004 refuses; `SameSite=Lax` is the second layer). The header is in
the CORS allow-list; bearer requests never need it.

`POST /api/v1/auth/logout` (`src/hullbreach_server/api/auth.py::logout`)
requires `Authorization: Bearer <token>` (via `get_current_user`) and
revokes it: `all=false` (the default query param, bound to the
`all_sessions` argument) revokes only the
presented session (`revoke_session`); `all=true` revokes every
non-revoked session for that user (`revoke_all_sessions`, T-0019). 204
No Content on success; 401 (via `get_current_user`) if the token is
already invalid, so logging out twice with the same token 401s the
second time. A cookie-authenticated logout (with the CSRF header) also
expires the cookie in the response.

`GET /api/v1/auth/session` (`src/hullbreach_server/api/auth.py::session`)
is the game-server-only verify call (ticket `~48H1VAK`): it requires a
valid `X-Server-Key` header (see Game-server keys below) and the player's
bearer token, and returns a `SessionInfo` (`user_id`, `role`) with 200 --
deliberately minimal, no `username`/`email`, since the game server's only
need is "who is this and what can they do" (T-0026). The key is checked
first, by a route-level `require_game_server` dependency, so a key problem
never reaches the token check. Once the key is accepted the token goes
through `get_current_user`, so a missing, malformed, expired, or revoked
token gets the same uniform 401 `{"detail": "not authenticated"}`. The
website never calls this route; it checks its own token with `GET /me`.

The game client authenticates the same way the browser does: it calls
`POST /api/v1/auth/login` verbatim (no separate route or client-kind
flag -- the design's `f_login_game` flow and `f_login_web` share the
identical `attr "POST /api/v1/auth/login"`), gets back the same
`LoginResponse`, and then presents that token to its own server, which
calls `GET /api/v1/auth/session` server-side, with its `X-Server-Key`, to
validate it and learn the player's id and role (T-0026). The login route
does not distinguish a game-client caller from a browser caller; only the
verify call is server-only.

### Game-server keys

The game server authenticates with a shared secret, not a player session
(T-0052). `AppConfig.game_server_api_keys` is a list of `SecretStr`s, read
from `HULLBREACH_GAME_SERVER_API_KEYS` (comma-separated; `.env.example`
lists it) or the `[tool.hullbreach_server]` table (there is no CLI flag,
the CLI only has `--host` and `--port`); the default is empty. The values
never appear in a `repr` or in logs. `require_game_server`
(`src/hullbreach_server/auth/server_keys.py`) is the FastAPI dependency a
game-server-only route lists: it reads the `X-Server-Key` header and
compares it with `check_server_key`, which returns a typani
`Result[None, ServerKeyError]` and compares every configured key with
`hmac.compare_digest` so timing does not reveal a match. Each error maps
to one response through `SERVER_KEY_REJECTIONS`, so a game server (and the
game doctor) can tell the cases apart from the body alone:

| Situation                                 | Status | `detail`                    |
| ----------------------------------------- | ------ | --------------------------- |
| platform has no keys configured           | 503    | `server key not configured` |
| request has no `X-Server-Key` header      | 401    | `server key missing`        |
| header does not match any configured key  | 401    | `invalid server key`        |
| key accepted, bearer token missing or bad | 401    | `not authenticated`         |

An unconfigured platform refuses with 503 rather than 401 because the
fault is on the platform operator's side, not the caller's: set
`HULLBREACH_GAME_SERVER_API_KEYS` and restart the API (the refusal is also
logged at ERROR naming that variable). A wrong key is logged at WARNING;
the presented value never is. FastAPI's default 403 for a missing header
is never used. The routes guarded by the dependency today are
`GET /api/v1/auth/session` (ticket `~48H1VAK`) and `POST /api/v1/matches`
(T-0054).

### Matches

`src/hullbreach_server/db/models/match.py` holds the record of a finished
match (T-0053). `Match` (table `matches`) has `id` (UUID), `winner_id` (FK
to `users.id`), `duration_seconds` and `created_at`; its `player_stats`
relationship lists the `MatchPlayerStats` rows (table `match_player_stats`),
one per player: `match_id` (FK to `matches.id`, `ON DELETE CASCADE`),
`user_id` (FK to `users.id`, indexed), and the `damage_dealt`,
`blocks_destroyed`, `blocks_placed` and `time_alive_seconds` counters, each
defaulting to 0. `(match_id, user_id)` is unique, so a player has at most
one stats row per match. The user FKs deliberately have no `ON DELETE`
action: deleting an account anonymizes the user row and keeps its matches
(T-0037), so a hard delete of a player with matches must fail. Currency payout lands with T-0070.

`RatingChange` (`db/models/rating.py`, table `rating_changes`, T-0057) is
one player's rating in one match: `match_id` (FK, `ON DELETE CASCADE`),
`user_id` (FK, indexed), `rating_before`, `rating_after` and `created_at`;
`(match_id, user_id)` is unique. A player's current rating is their latest
`rating_after`, else 1200 (`services/matches.py::current_rating`).

#### POST /api/v1/matches

The game server reports a finished match (T-0054). The route requires the
`X-Server-Key` header (see Game-server keys); a player bearer token alone is
a 401. The body is a `MatchReport` (`services/matches.py`, unknown fields
rejected):

```json
{
  "match_id": "<uuid, chosen by the game server>",
  "winner_id": "<uuid, one of the players>",
  "duration_seconds": 240,
  "players": [
    {
      "user_id": "<uuid>",
      "damage_dealt": 900,
      "blocks_destroyed": 14,
      "blocks_placed": 30,
      "time_alive_seconds": 240
    },
    {
      "user_id": "<uuid>",
      "damage_dealt": 400,
      "blocks_destroyed": 14,
      "blocks_placed": 30,
      "time_alive_seconds": 240
    }
  ]
}
```

`players` holds exactly two different users; every counter is a
non-negative integer (default 0). Only decisive matches are modeled, as in
the Elo section: `winner_id` is required, there is no draw or forfeit. The
platform locks both players, rates them with `rate_match` from their
`current_rating`, stores the `Match`, both `MatchPlayerStats` and both
`RatingChange` rows in one transaction, and answers with a `MatchRecord`:
`match_id`, `winner_id`, `duration_seconds`, `played_at` and `players`
(sorted by `user_id`), each with the counters plus `rating_before` and
`rating_after`.

`match_id` is the idempotency key. The first report answers 201; a repeat
of the same `match_id` with the same body answers 200 with the identical
stored record and rates nothing again, so a game server can retry safely.

| Situation                               | Status | Body                                  |
| --------------------------------------- | ------ | ------------------------------------- |
| recorded                                | 201    | `MatchRecord`                         |
| same `match_id`, same body (replay)     | 200    | `MatchRecord`, identical to the first |
| same `match_id`, different body         | 409    | `{"detail", "field": "match_id"}`     |
| a `user_id` has no account              | 404    | `{"detail", "field": "players"}`      |
| invalid body (winner not a player, ...) | 422    | FastAPI validation errors             |
| missing or wrong `X-Server-Key`         | 401    | `{"detail"}`                          |
| no server keys configured               | 503    | `{"detail"}`                          |

The match then appears in `GET /api/v1/me/matches` and in the profile's
`recent_matches` for both players.

### Database migrations

`hullbreach_server db upgrade` runs Alembic programmatically
(`db/migrate.py::upgrade_to_head`, with `build_alembic_config` pointing
`script_location` at the package's own `db/migrations/`), so it works from any
working directory; it resolves the URL through `AppConfig`, hands it to
`env.py` via `Config.attributes["database_url"]`, and a failure prints a clear
message and exits 1 (`MigrationError`) instead of a traceback. (`alembic.ini`
at the repo root remains for bare `alembic` runs and the tests.) `db seed` calls
`db/seed.py::seed(session)` (T-0008), which idempotently upserts (a changed
name or price is updated) `db/seed_items.json`'s catalog (120 cosmetic entries across 8
categories, matched by `slug` so a re-run never duplicates a row) into
a hand-declared `items` table (created by the fourth migration below,
T-0101; `seed.py`'s own `Table.create(checkfirst=True)` call is a no-op
wherever that migration has run and exists only for the unit-test
SQLite fixture, which builds its schema from `Base.metadata` rather
than running Alembic), and creates the first admin account
via `auth.passwords.hash_password` when no `User` with `role ==
Role.admin` exists, reading `HULLBREACH_ADMIN_USERNAME`/`_EMAIL`/
`_PASSWORD` and returning `Err(SeedError.MissingAdminPassword)` rather
than inventing one. Admin credentials are validated with the same bounds as
`RegisterRequest` (`InvalidAdminCredentials`), a username or email already used
by another account is `AdminConflict`, bad seed data is `InvalidSeedData`, and
a database error rolls back and returns `DatabaseFailure`: `seed` never
raises, so `db seed` always exits through its clean `db seed failed` path. `db/migrations/env.py::run_migrations_online`
resolves `HULLBREACH_DATABASE_URL` via `AppConfig` the same way every
other entrypoint does and runs against a caller-supplied connection
(tests) or a fresh engine; `run_migrations_offline` always refuses,
since only online (connected) migrations are supported for 0.1.0
(docs/design/sprint-1.md section 8, open question). Each revision file
under `db/migrations/versions/` is generated from `script.py.mako`, the
standard Alembic revision template `alembic revision` reads by
convention via `alembic.ini`'s `script_location`. The first revision
(`ba2efc248a9a_baseline_no_tables_yet.py`) is a no-op: its
`upgrade`/`downgrade` create and drop nothing, since no ORM model existed
yet at that point --
it establishes the revision chain later migrations build on. The second
revision (`0f6d70e4d209_create_users_table.py`, T-0015) creates the
`users` table matching `src/hullbreach_server/db/models/user.py::User`
exactly, so `compare_metadata` reports no diff after `db upgrade` runs.
The third revision (`550676f68926_create_sessions_table.py`, T-0019)
creates the `sessions` table matching
`src/hullbreach_server/db/models/session.py::Session` exactly, including
its FK to `users.id` (`ON DELETE CASCADE`) and the indexed `user_id`
column. The fourth revision (`abbcc4cb6b34_create_items_table.py`,
T-0101) creates the `items` table `db/seed.py` upserts into --
deliberately not backed by an ORM model yet (T-0066 owns that), so
`tests/system/test_build.py`'s `compare_metadata` check excludes it via
an `include_object` filter rather than reporting a false "extra table"
diff. The fifth revision
(`7d2c4a91e0b3_create_matches_tables.py`, T-0053) creates `matches` and
`match_player_stats` matching `db/models/match.py` exactly. The sixth
revision (`3b8e6f1c9d24_user_role_check_and_ci_unique.py`) adds the
`ck_users_role` CHECK the users migration only promised (SQLAlchemy's
`Enum(native_enum=False)` does not create one by default) and unique
indexes on `lower(username)` / `lower(email)`; it fails on existing rows
that already collide case-insensitively or hold an unknown role. The seventh revision
(`c41e5f7a9b02_create_rating_changes_table.py`, T-0057) creates
`rating_changes` matching `db/models/rating.py`. The eighth revision
(`d52f6a8b0c13_index_rating_changes_for_leaderboard.py`, T-0062) adds
`ix_rating_changes_user_id_created_at` on `rating_changes (user_id,
created_at)` for the leaderboard's latest-rating-per-player query. The ninth
revision (`e7a3b9c1d2f4_add_users_deleted_at.py`, T-0037) adds the nullable
`users.deleted_at` that marks an anonymized (deleted) account. The tenth
revision (`f1b6c2d8a3e5_create_designs_table.py`, S35) creates `designs`
matching `db/models/design.py`.

### Elo rating

`src/hullbreach_server/rating/elo.py` is the pure rating arithmetic (T-0056):
no database, no FastAPI, no clock. It is plain Elo with one fixed K-factor
for every account (`K_FACTOR = 32`, no higher K for new accounts), a
`STARTING_RATING` of 1200 and a `RATING_FLOOR` of 100; a match is decisive
(there is no draw). `expected_score(rating, opponent)` is the standard
logistic `1 / (1 + 10 ** ((opponent - rating) / 400))`. `rate_match(winner,
loser)` returns a typani `Result[MatchRatings, EloError]`: the winner gains
`K_FACTOR * (1 - expected)` rounded half up to an integer (so the gain is
never negative, and an upset pays more than an expected win), and the loser
loses the same integer amount but never drops below the floor. A rating
under the floor is `Err(EloError.BelowFloor)`, not a silent clamp. `tests/unit/test_elo.py` sweeps a grid of rating pairs plus a seeded
random sample (floor edges included) to check that the winner never loses
rating and the loser never gains. Applying
the result to stored ratings and attaching it to a match is later work
(T-0057).

### Leaderboard

`GET /api/v1/leaderboard?limit=` (T-0061, T-0062) is public: no key and no
token are needed, and the page works for a signed-out visitor. It ranks
every player with at least one `rating_changes` row by current ELO (the
`rating_after` of their latest change; ties break by username so the order
is total). `limit` is the number of rows, default and maximum 100; 0 or
more than 100 is a 422. The 200 body is `{entries, me, total_players}`:
`entries` are `{rank, user_id, username, rating, matches_played}` best
first, `total_players` is the field size, and `me` is the caller's own
entry (with their true rank, even when it is below the visible rows) when
the request carries a valid bearer token and the caller has played, else
null. An invalid or expired token is treated as anonymous, not a 401,
because the board is public (`auth/deps.py::get_optional_user`). A
database failure is a 503 `{"detail": "leaderboard unavailable"}`. The
logic is `services/leaderboard.py::leaderboard`, a typani `Result` over
one ranked window query; the index added by the eighth migration keeps
it off a full table scan. Open question from T-0061, kept at the story's
default: top 100 with no pagination and no minimum match count.

### Matchmaking queue

`/api/v1/queue` (S29, ~1KEGC1Y) pairs signed-in players into 1v1 matches.
Every call needs the player's bearer token (401 otherwise). This is the
contract the game client and the game server (mcnairrobotics, networking)
consume.

- `POST /api/v1/queue` joins at the caller's current rating (latest
  `rating_changes.rating_after`, else the starting 1200), frozen for the
  wait. Body-less. 200 with a `QueueStatus`; joining again while queued is a
  no-op that keeps the original place. 409 `{kind: "already_matched",
  detail}` if the caller still holds an unacknowledged match (see DELETE).
- `GET /api/v1/queue` polls; poll about once a second. 200 `QueueStatus`:
  `{state, rating, waited_seconds, window, match}`. `state` is `idle` (not
  in the queue), `queued` (`rating`, `waited_seconds` and the current
  `window` are set) or `matched` (`match` is set).
- `DELETE /api/v1/queue` always answers 204. It leaves the queue, and also
  acknowledges a made match: the client must call it once it has read a
  `matched` status (or abandoned it) before it may join again. Only the
  caller's own state is cleared; the opponent keeps theirs.

`match` is `{match_id, server_address, opponent_id}`. Both players of a pair
receive the same `match_id` (a UUID) and `server_address` (`host:port`, the
`game_server_address` setting / `HULLBREACH_GAME_SERVER_ADDRESS`, default
`127.0.0.1:7777`). The client connects to `server_address` and presents the
`match_id`; the game server later reports the result with
`POST /api/v1/matches` using that same `match_id`, which is how a queue
match becomes a rated match. A made match is readable for 120 seconds, then
forgotten.

Pairing is nearest-rating-first within a widening window. A player accepts
an opponent whose rating differs by at most `100 + 50 * floor(waited / 5s)`
points; a pair forms when the gap is within the larger of the two players'
windows, and each player (longest waiter first) takes the closest rating in
reach, ties to the earlier joiner. Pairing runs on every join and poll, not
on a timer, so a status poll is what lets a widened window take effect.

Assumptions: the queue is in memory and process-local, so a restart empties
it and the API must run one process per queue (a shared store is the later
step); there is no cap on the window, so every waiter is eventually paired
when two or more are queued; the game server has no lookup of queue
matches yet, only the `match_id` echo above. The logic is
`services/matchmaking.py::MatchmakingQueue`, a thread-safe class with an
injectable clock; the routes are in `api/matchmaking.py`.

## Web frontend

The React app under `web/` is the player-facing site: landing page, cookie
notice and data policy, registration and login, the profile page, and the
cosmetic store. `web/index.html` is vite's entry; it loads
`web/src/main.tsx`, which mounts `web/src/App.tsx` and imports the
Tailwind stylesheet `web/src/index.css`. In development vite proxies
`/api` to the Python server so the site and the API share an origin.

The design system is declared once in `crunk.toml` (palette, spacing and
type scales, radii, z-index layers, file organization). `crunk tokens`
generates `web/src/styles/tokens.css` and `web/tailwind.theme.json` from
it; `web/tailwind.config.ts` hands that theme to Tailwind through
`@config`, and `crunk check` lints every stylesheet and `className` string
against the spec so an undeclared color or off-scale spacing is a red
build. Utilities are namespaced to the declared scales: `bg-paper`,
`text-ink`, `gap-space-8`, `text-font-size-20`, `rounded-radius-4`.

### Routing and page shell

`web/src/router.tsx` builds a `createBrowserRouter` data router: `/` (the
landing content), `/register`, `/login`, `/leaderboard` (public), `/me` (the profile page), `/me/matches`, `/settings`, `/data-policy`, `/cookie-policy`, and a `*` not-found fallback, all
routed as children of `web/src/App.tsx`'s page shell. `App` renders
`Header`, the `CookieNotice`, the routed `Outlet`, and `Footer` -- and stays renderable with no
`Outlet` match (or no router at all) since a bare `<Outlet/>` outside a
router context renders nothing rather than throwing. `web/src/main.tsx`
mounts the tree with `RouterProvider`, not `App` directly.

`web/src/components/Header.tsx` reads `useSession()` (below) and shows
a public Leaderboard link, then Register/Log in links when signed out, or Profile, Matches and Settings
links, the username and a bordered Log out control when signed in; the
link for the page being shown carries `aria-current="page"` and a cyan
underline, and every page shows a `Breadcrumb` trail above its title; every control is a real `<a>`/`<button>` (never a
`<div onClick>`) so tab order and Enter-activation work by construction.
The signed-in Log out control calls `api/auth.ts`'s `logout()` with the
session's token (best-effort: an expired token or a network error does
not block signing out locally), then `clearSession()`, then navigates
home -- sign-out clears the in-memory session. `web/src/components/Footer.tsx` links to the
cookie and data policy pages.

Every internal link is an `AppLink` (`web/src/components/AppLink.tsx`) and
every programmatic move (after login, logout, the brand mark) goes through
`navigate()` in `web/src/components/navigate.ts`: `history.pushState` plus
a `popstate` event the data router listens to. A plain `<a href>` or
`window.location.assign` would reload the document and drop the in-memory
session (see Session persistence), so the header, footer and login flow
never do. Modifier and middle clicks on an `AppLink` fall through to the
browser so open-in-new-tab still works. `usePathname()` is the matching
hook the header uses for `aria-current`.

### Landing and policy pages

`web/src/pages/Landing.tsx` is the `/` page: the premise, sign-in calls to
action (Create account and Log in when signed out, Profile and Match history
when signed in), a Download panel and the four beats of a match. No game
build is published yet, so the panel says so instead of linking a file; it
becomes a link when the release ticket lands.

`web/src/components/CookieNotice.tsx` renders once in the page shell. It
stores `hullbreach.cookie-notice` = `dismissed` in `localStorage` when the
visitor clicks Dismiss and stays hidden on later loads; if storage is
blocked it still hides for the current page load.

`/data-policy` (`DataPolicy`) has Stored data, Purpose and Deletion
sections, and `/cookie-policy` (`CookiePolicy`) names the one strictly necessary
`hullbreach_session` cookie (opaque token, HttpOnly, SameSite=Lax, cleared
on logout) and the localStorage notice flag; `CookieNotice` says the same
in one sentence.
Both are built from `PolicySection` and linked from the footer. The text
only describes data the server really stores (account fields, match stats,
session records); there is no self-service deletion, so the policy says to
ask the maintainers.

### Visual design rules

The site reads as a blueprint / technical drawing of a spaceship: dark
navy paper, cyan hairlines, one signal orange. These rules are enforced,
not suggested:

- Palette: `crunk.toml` declares paper `#0B1620`, panel `#0F1D2A`, ink,
  muted, a pre-mixed hairline, cyan `accent` and signal orange. Orange is
  reserved for the primary button, the ELO number and losses/alerts; there
  is no purple and no gradient text. The page background is a grid-paper
  tile (`web/public/grid.svg`, referenced from `reset.css`).
- Corners: radius 0 everywhere (`RADIUS001` is an error); boxes are
  square with 1px hairlines.
- No decoration for its own sake: `web/tests/unit/designRules.test.ts`
  fails on gradient, shadow, blur, backdrop and gradient-text utilities in
  `className` strings, on `gradient`/`box-shadow`/`text-shadow`/
  `backdrop-filter`/`blur()` in stylesheets, and on any non-ASCII
  character anywhere under `web/src`. There are no title blocks,
  dimension dividers or registration marks.
- Type: Audiowide (solid, uppercase, tracked, `font-display`) only for the
  wordmark and h1/h2; IBM Plex Mono for labels and numbers; IBM Plex Sans
  for prose. All three are self-hosted through `@fontsource` packages
  imported in `web/src/main.tsx` with `font-display: swap`; nothing loads
  from a CDN. Tokens: `--font-family-base`, `--font-family-mono`,
  `--font-family-display` in `web/src/styles/tokens.css`.
- Focus: `web/src/styles/base/reset.css` draws one keyboard-only accent
  outline, offset 2px, on every control.
- Contrast: every text/background pair is a `[roles]` entry in
  `crunk.toml`, checked to WCAG AA by `crunk check`. Minimum text is 12px.
- Layout: each page has one purpose and one primary action. A page is a
  left-aligned column: breadcrumb ("you are here"), display-face h1, a
  one-line purpose, then content. Every chart and drawing sits inside a
  bordered, padded `Panel`/figure that clips (`overflow-hidden`), uses
  inset coordinates and `vector-effect="non-scaling-stroke"`, so nothing
  touches or crosses its frame at 1280 or 390px.
- Panels: `Panel` is a hairline box (`tone="primary"` for the one cyan
  panel a page is about) with an optional label chip set into its top
  border. Ratings and stats are mono `tabular-nums`; Win/Loss is a word
  plus a colored left edge, never color alone. Touch targets are at least
  44px tall.
- Motion: 120ms color/border easing on links, buttons and inputs only,
  and only under `prefers-reduced-motion: no-preference`.
- States: every data page has Loading plus `SkeletonRows`, an
  `EmptyState` with a next step, and an error `Notice` with Try again.
- Shared components, not one-offs: `Page` and `Breadcrumb` (shell,
  trail, title, purpose), `Button` / `ButtonLink` (orange primary,
  cyan-outline secondary), `TextField` (label, hint, error tied by
  `aria-describedby`, `aria-invalid`), `Notice` / `Loading`, `AppLink`,
  `HullReadout` (the landing page's side-view spaceship line drawing),
  `EloTrace` (ELO over the last matches; fewer than two ratings shows a
  hatched "no data yet" placeholder), plus `Panel` / `StatTile` /
  `SectionHeading` / `EmptyState` / `SkeletonRows`
  (`web/src/components/Readout.tsx`).
- Copy is concrete and terse: name the thing (ELO, match history, hull),
  never "seamless", "unleash" or "get started today". The setting is
  space, so no sea or naval wording.

### Session persistence

`web/src/auth/session.ts` is the client-side session store: a
`StoredSession` (token/userId/username/role) held in module memory only
and never written to `localStorage`, `sessionStorage` or a script-readable
cookie (INV-006), so injected script cannot read the bearer token back from
storage. `saveSession`/`loadSession`/`clearSession` read and write that
variable; `useSession` is the React hook (`useSyncExternalStore`) `Header`
and any consumer read it through, re-rendering on login, logout and profile
updates. A reload no longer signs the user out: `main.tsx` awaits
`restoreSession()` before first render, which calls `GET /api/v1/me` with
the server's HttpOnly `hullbreach_session` cookie (`credentials: "include"`,
3 s budget) and, on 200, saves a session whose `token` is `""` (the cookie
authenticates; `bearerHeaders("")` sends no header). On 401, a timeout or an
unreachable server it stays signed out and the app renders normally. There is
no cross-tab sync. In dev the vite proxy keeps `/api` same-origin, so the
cookie needs no CORS.

### Auth API client and the register page

`web/src/api/auth.ts` is the one `fetch` wrapper every auth-facing page
uses (docs/design/sprint-1.md sec.5/6): `register`/`login` POST their
request body and resolve to a `UserProfile`/`LoginResponse`; `logout`
sends a `Bearer` `Authorization` header (or relies on the cookie). Every
request goes through `apiFetch`, which adds `credentials: "include"`, the
`X-Hullbreach-Web` CSRF header and an `AbortController` timeout (10 s default,
`REQUEST_TIMEOUT_MS`); a timeout or network failure rejects with `ApiError`
status 0 (~R5PHHZC). There is deliberately no client
for `GET /api/v1/auth/session`: that route needs a game-server key a
browser never holds, so the website checks its token with `GET /me`. Any non-2xx
response is normalized into a thrown `ApiError {status, detail, field?}`
-- `field` is present only when the server named one (409's duplicate
username/email), letting a caller show the error next to that field
specifically rather than as a generic banner.

`web/src/pages/Register.tsx` is the first such caller: it keeps a
`fieldErrors` map and, on submit, calls `register()`. An `ApiError` with
a `field` sets that field's error (rendered via `aria-describedby`
pointing at a `<p id="{field}-error">` beneath the input, so a test can
find it either way); an `ApiError` with no `field` (422's generic
validation failure) sets a `role="alert"` form-level banner instead.
Success swaps the form out for a confirmation message.

`web/src/pages/Login.tsx` is the second caller: on submit it calls
`login()`, and on success builds a `StoredSession` from the returned
`LoginResponse` (`token`, and `userId`/`username`/`role` from its
`user`), passes it to `saveSession` (`web/src/auth/session.ts`), and
navigates home -- keeping the token in memory only (INV-006),
and `useSession` reflects it immediately in the same page load. Any
`ApiError` (401 invalid credentials, 429 rate-limited) sets a
`role="alert"` form-level banner with the server's `detail` message;
Login has no field-level errors (the login contract never names a
`field`).

### Player API

`src/hullbreach_server/api/me.py` serves the signed-in player's own
resources under `/api/v1/me`; every route requires `Authorization: Bearer
<token>` and answers the uniform 401 `{"detail": "not authenticated"}`
through `get_current_user`. The response models live in the service layer
(`src/hullbreach_server/services/`), which turns ORM rows into the shapes
`web/src/api/me.ts` names.

`GET /api/v1/me` (`api/me.py::get_me`, T-0031) returns a `MeResponse`
(`services/profile.py::build_me`): the `UserProfile` fields (`id`,
`username`, `email`, `role`, `currency`, `rating`, `created_at`) plus
`inventory` (a list of `OwnedSkin` `{id, slug, name}`) and
`recent_matches` (the newest five `MatchSummary` rows). Two sections are
honest defaults until their models land: `inventory` is always `[]` (no
Item/Inventory ORM model or ownership table yet, T-0066), and `currency`
is `0` and `rating` is the player's current ELO (see Auth API).

A `MatchSummary` (`services/matches.py`) is one match from the player's
point of view: `id`, `played_at` (the match's `created_at`), `opponent`
(the other players' usernames, comma-joined, or `unknown`), `result`
(`win` when `winner_id` is the player, else `loss`), `duration_seconds`,
`rating_before`, `rating_after` and `stats` (the player's own
`damage_dealt`, `blocks_destroyed`, `blocks_placed` and
`time_alive_seconds`). Matches are ordered newest first by
`(created_at, id)`. `rating_before` and `rating_after` come from the
player's `RatingChange` row for that match (see Matches); a match with no
row (none is recorded outside `POST /api/v1/matches`) shows the starting
rating (1200) for both.

`PATCH /api/v1/me` (`api/me.py::patch_me`, T-0034) edits the player's
`username`, `email` and `password`. The body is an `UpdateMeRequest`
(`auth/schemas.py`): every field optional, the same bounds as register,
`email` lower-cased, and unknown fields (such as `role`) rejected with
a 422. A new email or password must also carry `current_password`;
missing or wrong it is a 403 `{"detail": "current password required" |
"current password is incorrect", "field": "current_password"}`. A
username or email already held by another account (case-insensitive) is
a 409 `{"detail": "username already taken" | "email already taken",
"field": ...}`. `services/profile.py::update_profile` returns a typani
`Result[User, ProfileUpdateError]`; on a password change it re-hashes the
password and revokes every other session of the player, keeping the one
that made the request. The response is the updated `UserProfile`.

`GET /api/v1/me/matches?cursor=&limit=` (`api/me.py::get_my_matches`,
T-0059) returns a `MatchPage` `{items, next_cursor}` of `MatchSummary`
rows, newest first (`services/matches.py::match_page`). Paging is keyset,
not offset: `next_cursor` is an opaque URL-safe token encoding the last
row's `(created_at, id)`, and the next page is the rows strictly after
that key, so a match recorded while the player pages never shifts or
repeats a row. `next_cursor` is null on the last page (one extra row is
fetched to know, no COUNT). `limit` defaults to 20 and is bounded 1..100
(422 outside). A cursor that does not decode is a 422 `{"detail":
"invalid cursor", "field": "cursor"}`. A player with no matches gets
`{"items": [], "next_cursor": null}`. `tests/system/test_account_flow.py`
drives register, login, `GET /me`, `PATCH /me`, `GET /me/matches` and
logout through `create_app` on an Alembic-migrated database.

`DELETE /api/v1/me` (`api/me.py::delete_me`, T-0037) deletes the caller's
account. It needs auth (a bearer token, or the session cookie plus the
`X-Hullbreach-Web` CSRF header) and a `DeleteMeRequest` body
`{"current_password"}`; a missing password is a 422 and a wrong one is a 403
`{"detail": "current password is incorrect", "field": "current_password"}`
that changes nothing. `services/account_deletion.py::delete_account` returns
a typani `Result[None, DeleteError]`. On success the user row is anonymized,
never removed: the username becomes `deleted-<24 hex of the id>`, the email
`<that>@deleted.invalid`, the password hash an unusable random one, the role
`player`, and `deleted_at` is stamped. Every session row of the user is
deleted, so old tokens are 401, and the response is 204 with the session
cookie cleared. Matches, stats and rating changes are kept; wherever another
player sees a deleted user's name (`GET /me/matches` opponent, the
leaderboard) it is the placeholder `deleted player`
(`services/matches.py::display_name`). The old username and email are freed
for new registrations.

### Ship designs

`/api/v1/designs` stores a player's saved ship designs (S35,
`api/designs.py`, `services/designs.py`, `db/models/design.py`). Every route
needs a bearer token and is owner-only: another player's design is a 404,
the same as a missing one. `GET /designs` lists the caller's designs (id,
name, format_version, block_count, updated_at; newest update first),
`POST /designs` creates one (201), `GET /designs/{id}` returns it with the
design JSON, `PUT /designs/{id}` replaces name and design, and
`DELETE /designs/{id}` answers 204. The body is `{name, design}` where
`name` is 1..64 characters and `design` is the game's `BlockGridDesign`
object.

Validation mirrors `BlockGridDesign.cs`: `version` must be 1 (422 on
`design.version` otherwise), 1..4096 blocks, grid coordinates -128..127,
`mods` 0..255, a non-empty `type` string, no two blocks on one cell, no
unknown keys, nesting of at most 6. The compact JSON text may be at most
1048576 characters; larger is a 413 whose detail names that limit. A player
may keep 50 designs; the 51st create is a 409. Errors are `{detail, field}`.
The server does not check block type names or connectivity; the game owns
those. The service returns typani `Result[T, DesignError]` and the router
maps `DesignError.kind` to the status. The `designs` table is created by
`f1b6c2d8a3e5_create_designs_table.py`.

### Player API client and the profile page

`web/src/api/me.ts` is the client for the signed-in player's own
resources under `/api/v1/me`. It reuses `api/auth.ts`'s `requestJson`
(one `fetch` wrapper, one `ApiError` shape) and `bearerHeaders`. The
`MeResponse` type is the contract of `GET /api/v1/me` (T-0031, see
Player API): the `UserProfile` fields (`currency` is the balance, `rating`
the Elo) plus `inventory` (owned skins) and `recent_matches` (newest
first). `MatchSummary` is shared with the match history (T-0059). The
shared fixture `web/tests/fixtures/me.ts` is a typed instance of that
contract, so pages are tested without a server.

`web/src/pages/Profile.tsx` is routed at `/me`. It reads the token from
`useSession()`; signed out it shows a log-in link and makes no request.
Signed in it loads `fetchMe` and renders the username, rating, currency,
owned skins and at most five recent matches (`web/src/components/
MatchItem.tsx`, one row per match), or an empty-state line for each empty
section. A rejected request shows the server's `detail` in a `role="alert"`
paragraph. The layout is a single column capped at 40rem with wrapping
flex rows, and every user-supplied string carries `wrap-anywhere`, so it
fits a 400px phone. jsdom has no layout engine, so the test asserts that
contract (`web/tests/support/layout.ts` `overflowRisks`: no fixed width
above the viewport, no unwrappable text) rather than measuring
`scrollWidth`.

The live-server test in `web/tests/unit/Profile.test.tsx` runs the real
client (register, log in, `fetchMe`) against a running API when
`HULLBREACH_LIVE_API` holds its origin (for example
`HULLBREACH_LIVE_API=http://127.0.0.1:8001 npm test`) and is skipped
otherwise.

The profile has one primary `Panel` (label "ELO"): the large orange
rating next to an `EloTrace` built from `recent_matches` (oldest
`rating_before`, then each `rating_after`, chronological). A quieter
"Summary" panel holds "Last 5" (wins-losses) and "Net ELO", computed
client-side from the same five matches and shown only when matches exist,
and Balance. The primary action is "View match history". Loading shows
`SkeletonRows`, empty skins and matches are `EmptyState`s, and a failed
request is an error `Notice` with Try again.

### Account settings page

`web/src/pages/Settings.tsx` is routed at `/settings` and edits the
signed-in player's display name (the username), email and password through
`updateMe` in `web/src/api/me.ts`, which is `PATCH /api/v1/me` (T-0034,
see Player API; the page's tests use the fixture `profileFixture` in
`web/tests/fixtures/me.ts`). It copies Register's
inline-error pattern: an `ApiError` with a `field` is shown beside that
input through `aria-describedby`, and one without becomes a `role="alert"`
banner. The contract: the request carries only the changed fields,
a new email or password also carries `current_password`, and a wrong one is
a 403 naming `field: "current_password"`. The page enforces the same rule
locally (an email or password change with no current password is refused
inline without a request) and says "Nothing to change." for an untouched
form. On success it clears the secret fields and writes the new username
into the stored session so a reload shows it. Signed out, the page renders
`web/src/components/SignInPrompt.tsx`, the log-in prompt the profile page
now shares. The fields sit in a `Panel` under Identity and Credentials
fieldsets, and password inputs get a Show/Hide toggle (`aria-pressed`,
deliberately not named "password" so label queries stay unambiguous).

Below the form a "Danger zone" `Panel` holds account deletion (`deleteMe`
in `web/src/api/me.ts`, `DELETE /api/v1/me` with `{current_password}`).
"Delete account" opens a confirm step asking for the password; an empty
password is refused locally, a 403 shows the server's detail as a
`role="alert"` banner and keeps the session, and a 204 clears the in-memory
session and navigates to `/` (the server clears the cookie). The data
policy page's Deletion section describes this flow.

### Match history page

`web/src/pages/History.tsx` is routed at `/me/matches` and lists the
signed-in player's matches, newest first, through `fetchMatches` in
`web/src/api/me.ts`: `GET /api/v1/me/matches?cursor=` (T-0059, see
Player API; the page's tests use `makeMatchPage` in
`web/tests/fixtures/me.ts`).
A `MatchPage` is `{items, next_cursor}`; `next_cursor` is null on the last
page. Each row is `web/src/components/MatchItem.tsx` in `detailed` mode
(opponent, result, rating before and after, date, duration and stats).
A `MatchColumns` strip (a div, so the list keeps one `li` per match)
labels the columns on wide screens, and an "N loaded" readout under the
list counts what is shown (the API has no total). `SkeletonRows` fill the
first load and an `EmptyState` replaces the list when there are no matches.
Load more requests the next cursor and appends the page; the control is
disabled while a request is in flight, vanishes when the cursor is null,
and after a failed request stays as a retry (labelled Try again if the
first page failed) with the matches already loaded kept. Responses that
belong to an earlier list (StrictMode's double-run effects, a changed
token) are dropped, so no match is listed twice. The page does not
virtualize the list; it relies on the server's page size to keep the DOM
small, and the page size is the server's default (no `limit` is sent).

### Leaderboard page

`web/src/pages/Leaderboard.tsx` is routed at `/leaderboard`, is public, and
lists the top players by ELO through `fetchLeaderboard` in
`web/src/api/leaderboard.ts`: `GET /api/v1/leaderboard` (T-0062; the tests
use `makeBoard` in `web/tests/fixtures/leaderboard.ts`). The response is
`{entries, me, total_players}`. A signed-in player's token is sent, so the
server also returns `me`: their own rank. Their row is highlighted
(`aria-current`, accent border, a "You" tag); when they are outside the top
list, a "Your rank" row is added below it. The ELO is the one orange
(`signal`) figure in each row. A footer reads "N shown of M ranked".
`SkeletonRows` fill the first load, an `EmptyState` replaces the list when
nobody is ranked, and a failed request shows an alert with Try again.
Stale responses (StrictMode's double-run effects, a changed token) are
dropped. The page does not paginate; it shows the server's default top 100.

## Operator scripts and the doctor

`src/hullbreach_ops/` is the operator tooling a person runs on their own
computer: the doctor and the start/stop/demo scripts (tickets `~99XSJ66`
and `~X4SRPKM`). It is a separate package from `hullbreach_server` on
purpose: it is the only code that runs other programs (docker, git, npm,
uv), and INV-007 forbids `subprocess` under `src/hullbreach_server/**`.
`frob.toml`'s `POL-ops-outside-server` rule and
`tests/unit/test_ops_boundary.py` keep the request-handling code from
importing it; only `hullbreach_server.__main__` does, and `hullbreach_ops/cli.py`
imports the command modules lazily. Every program call goes through
`proc.py` with an argv list, never a shell string.

Each script is one implementation behind three entry points: the
subcommand (`uv run hullbreach_server <command>`), the Makefile target of
the same name, and, for the doctor, the wrappers `doctor.sh` (macOS, Linux,
WSL) and `doctor.cmd`/`doctor.ps1` (Windows, which explain how to get into
WSL and then hand over to `doctor.sh`). The wrappers only make sure git,
uv, Docker and Node.js exist and offer their official installers after a
`[y/N]` question; every real check is in Python.

| Command      | What it does                                                                                                                                  |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `doctor`     | runs the checks below; `--demo website/guest/platform/online`, `--only <check>`, `--collect`                                                  |
| `demo`       | everything for the class demo in one go: creates `.env` with generated secrets if missing, then `start`, then the demo accounts and history   |
| `demo-match` | posts one sample match as the game server (first configured key): `demo_pilot` beats a fresh rival, prints the rating before and after        |
| `smoke`      | front-to-back check of a running stack: register, log in, profile, history, game session check, log out (through the website's proxy)         |
| `start`      | database container (waits for healthy), migrations, seed, API and website in the background                                                   |
| `stop`       | stops what `start` began (process ids in `.hullbreach/run/`) and the container; data is kept                                                  |
| `status`     | what is running, on which port                                                                                                                |
| `reset-db`   | deletes this compose project's database volume and recreates it; needs a terminal and the volume name typed back                              |
| `demo-users` | registers `demo_pilot_1` and `demo_pilot_2` through the API; the password is typed or generated and shown once                                |
| `server-key` | generates a game-server key and says where it goes on both sides; never written to disk                                                       |
| `lan`        | `start` bound to `0.0.0.0`, prints the addresses to share, and on WSL the Windows port-forward and firewall commands (run only after `[y/N]`) |
| `console`    | tails the API log as readable request lines; `--db` adds database changes ([Demo console](#demo-console))                                     |

Terminal output goes through `console.py`'s `Console`, not logging: every
line is redacted (registered secret values plus anything that looks like a
credential) and kept as a transcript. Log records go to
`.hullbreach/logs/ops.log`; the API and website started by `start` write
`api.log` and `web.log` next to it. `doctor --collect` zips the redacted
transcript, the redacted ends of those logs and a few facts about the
computer into `hullbreach-support-<timestamp>.zip`; it never includes
`.env` or any setting value.

Where things run comes from environment variables (or `.env`, loaded by
`load_dotenv` in `__main__`), read by `settings.py::OpsSettings`:
`HULLBREACH_PORT` (API, default 8000, also read by the server and by
`vite.config.ts` for its `/api` proxy), `HULLBREACH_WEB_PORT` (website,
5173), `HULLBREACH_DB_PORT` (host side of the compose port mapping, 5432),
`HULLBREACH_HOST` and docker's own `COMPOSE_PROJECT_NAME`. Together they
let a second copy of the stack run beside the first.

The doctor (`doctor.py`) runs the checks of `REGISTRY` in order. Each
returns a `CheckResult` (PASS, WARN, FAIL or PENDING, a one-line summary,
numbered fix steps and a README section from `readme_links.py`, whose
anchors `tests/unit/test_ops_readme_links.py` checks). A check lists the
checks it needs; when one of those FAILs it is shown as PENDING instead of
running, but the whole checklist is always printed, followed by the first
FAIL to fix. The doctor never reads `.env` itself: `env-file` checks only
that it exists, and `settings` loads it through `AppConfig` and reports
each setting as set or not set, never its value.

| Check id        | Needs                           | Checks                                                                                                                  |
| --------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `os`            |                                 | operating system, WSL detection                                                                                         |
| `git`           |                                 | git installed                                                                                                           |
| `repo`          | `git`                           | inside the checkout, up to date with its upstream                                                                       |
| `uv`            |                                 | uv installed                                                                                                            |
| `python`        | `uv`                            | the Python version the project needs                                                                                    |
| `py-deps`       | `python`                        | `uv sync` done and current                                                                                              |
| `node`          |                                 | Node.js and npm match `.nvmrc` / `engines`                                                                              |
| `web-deps`      | `node`                          | `npm ci` done and current                                                                                               |
| `docker`        |                                 | Docker installed                                                                                                        |
| `docker-daemon` | `docker`                        | the Docker engine is running                                                                                            |
| `env-file`      |                                 | `.env` exists (WARN when settings come from the environment instead)                                                    |
| `compose-file`  | `docker`                        | `docker compose config` accepts `docker-compose.yml`                                                                    |
| `settings`      | `py-deps`                       | the server's own settings loader accepts the settings                                                                   |
| `game-keys`     | `settings`                      | `HULLBREACH_GAME_SERVER_API_KEYS` set (needed by the platform demo)                                                     |
| `ports`         |                                 | API, website and database ports free or held by this stack; names the holder                                            |
| `db-container`  | `docker-daemon`, `compose-file` | the database container is up and healthy                                                                                |
| `db-connect`    | `db-container`, `settings`      | the API's database URL connects                                                                                         |
| `migrations`    | `db-connect`                    | the schema is at the Alembic head                                                                                       |
| `seed`          | `migrations`                    | the item catalog is loaded (WARN when there is no admin)                                                                |
| `api`           | `migrations`, `py-deps`         | `/api/v1/health` answers (the doctor starts the API if needed)                                                          |
| `web`           | `web-deps`, `api`               | the website and its `/api` proxy answer                                                                                 |
| `e2e`           | `api`, `seed`                   | register a throwaway `doctor-<timestamp>` user, login, `GET`/`PATCH /me`, `/me/matches`; the user is deleted afterwards |
| `game-session`  | `e2e`, `game-keys`              | `GET /api/v1/auth/session` refuses without a key and accepts a configured one                                           |
| `lan`           | `api`                           | whether other computers can reach the API, and what is in the way                                                       |

Services the doctor starts for a check (`api`, `web`) are stopped again
when the run ends. `--demo website` skips `game-keys`, `game-session` and
`lan`; `--demo guest` and `--demo online` need nothing from the platform
and point to the game's doctor; `--demo platform` runs everything and
ends with the values the game server and clients need.

### One-command demo

`uv run hullbreach_server demo` (or `make demo`) takes a fresh checkout to a
working browser -> website -> API -> database stack in one step, and
`make stop` stops it. `hullbreach_ops/demo.py` runs, in order:

1. `ensure_env`: when `.env` does not exist, copy `.env.example` with a
   generated database password (also inside the database URL), admin
   password and game-server key, mode 0600. If `HULLBREACH_DB_PORT` or
   `HULLBREACH_WEB_PORT` is set in the environment, the new file uses it,
   including the port in the database URL and the CORS origin (a bad port
   is rejected earlier, when settings load). An existing `.env` is never
   touched, and no secret value is printed.
2. `lifecycle.start`: database, migrations, catalog and admin seed, API,
   website (see the table above).
3. `seed_demo_data`: the player `demo_pilot` (password `demo-password-123`,
   published on purpose: the database listens on 127.0.0.1 only) with two
   opponents, `demo_rival` and `demo_ace`, and six matches of history. Each match goes through
   `services/matches.py::record_match` (backdated one to six days) with a
   fixed match id, so ratings evolve from 1200 and history shows real
   `rating_before`/`rating_after` and stats. Idempotent: a re-run replays the
   same ids and changes nothing.

If a database volume from an earlier setup is present, the freshly
generated password will not match it. The database then rejects the
login, and `demo` says so and offers the two ways out (restore the old
`.env`, or `reset-db`); it never deletes a volume itself.

`smoke` (`make smoke`, `hullbreach_server smoke`, `smoke.py`) is the
scripted check that the demo really works: through the website's `/api`
proxy it registers a throwaway `smoke_<hex>` account, logs in, reads
`/me` and `/me/matches`, calls the game-facing `GET /api/v1/auth/session`
with the first configured server key (skipped when none is set), logs out
and confirms the token no longer works. When a server key is set it also
registers a rival, posts a match (the smoke player wins) to
`POST /api/v1/matches` with that key and requires `/me`'s rating to rise. It stops at the first failing step
and prints no password, token or key.

`demo-match` (`make demo-match`, `demo_match.py`) is the no-curl way to
play the game server in the demo: it logs in as the seeded `demo_pilot`,
registers a fresh `rival_<hex>`, posts a pilot win to `POST /api/v1/matches`
with the first key in `HULLBREACH_GAME_SERVER_API_KEYS`, and prints the
pilot's rating before and after. It fails with fix steps when no key is
set. The step-by-step show is [docs/demo-script.md](demo-script.md).

### Demo console

`make console` (or `uv run hullbreach_server console`) tails the API log
(`.hullbreach/logs/api.log`, written by `make demo`) in a readable form so
an audience can watch requests arrive. `make console-db` (`--db`) also
shows the database changes the API makes. Options: `-n N` (lines of
history, default 10), `--no-follow` (print and exit). Ctrl+C stops it.

The API writes two kinds of line (`hullbreach_server/logging/events.py`,
`app/access_log.py`):

- `[access]`: one per request with time, method, path, status, duration,
  the signed-in user id or `-`, and whether the request carried a game
  server key (only its presence, never the value). Health polls are skipped.
- `[event]`: one per database state change at INFO: user registered, login
  ok/failed, logout and session revoked, match recorded (winner and rating
  before -> after per player), idempotent replay, settings updated (field
  names only, never values).

Console format: `HH:MM:SS  METHOD  path  status  NNms  user=..  [server-key]`,
and with `--db` `HH:MM:SS  DB      <text>`. Warnings and errors (such as a
failed login) always show. Times are UTC. Passwords, tokens and keys are
never logged. App-level event lines were chosen over Postgres statement
logs because they need no database configuration and read as plain
sentences.

## Sprint 1 design

`docs/design/sprint-1.md` is the system design for milestone 0.1.0
(database wiring, auth, and the site shell): module map, data model,
config, CLI, auth contracts, web routing, and a per-acceptance-criterion
test plan. `design/hullbreach.strata` is its checked companion model
(nodes, flows, and secrets for the same target architecture).
