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
to `App`, which runs uvicorn. Running with no subcommand still serves; a
`db` subcommand group (`db upgrade`, `db seed`) instead runs the given
database maintenance step and exits without building `App`/`create_app`.
Before serving, `App.__call__` fails fast: it builds an engine from
`AppConfig.database_url` and runs `check_connectivity`, exiting non-zero
and logging the connectivity error at `ERROR` instead of calling
`uvicorn.run` against a database it cannot reach.
`create_app` is the pure, socket-free core that
tests exercise through `TestClient`. Routes live in `api/`, one module per
resource, each exposing a `router` that `api_router` mounts under `/api/v1`;
`health` is the liveness probe, which never touches the database; `ready`
is the readiness probe, returning 200 with `{"status": "ready", "database":
"ok"}` when `check_connectivity` succeeds against the request's database
session, or 503 with `{"status": "not_ready", "database": "unreachable"}`
otherwise. The `logging` subpackage provides
`get_logger`, wired per the house logging convention (stdout for DEBUG/INFO,
stderr for WARNING+).

The `db` package is the SQLAlchemy 2.x surface: `create_db_engine(url)`
builds an `Engine` (normalizing a bare `postgresql://` URL to the
`psycopg` v3 driver), `check_connectivity(engine)` runs `SELECT 1` and
returns a typani `Result[None, DatabaseError]` whose message names the
host/port/database but never a raw URL or password, and `Base` is the
shared `DeclarativeBase` (with the ix/uq/ck/fk/pk naming convention) that
every ORM model and the Alembic env import. `get_engine`/`get_sessionmaker`
lazily build the process-wide engine and sessionmaker from
`AppConfig.from_external()`, and `get_db` is the FastAPI dependency that
yields a session per request and closes it afterward.

`src/hullbreach_server/db/models/user.py` holds the first ORM model:
`User` (table `users`) -- `id` (UUID), unique `username`/`email`,
`password_hash`, a `role` (`Role.player` default, stored as a `VARCHAR`
with a CHECK constraint via `native_enum=False` rather than a Postgres
native enum), and `created_at`.
`src/hullbreach_server/auth/passwords.py` provides `hash_password`/
`verify_password`, Argon2id via `pwdlib.PasswordHash.recommended()`.

### Auth sessions

`src/hullbreach_server/db/models/session.py` holds `Session` (table
`sessions`) -- `id` (UUID), `user_id` (FK to `users.id`, `ON DELETE
CASCADE`, indexed), a unique `token_hash` (sha256 of the bearer token,
hex-encoded; the plaintext token is never stored), `created_at`,
`expires_at`, and a nullable `revoked_at`. A session is valid iff
`revoked_at is None and expires_at > now()`. Those two timestamp columns
use the private `_UTCDateTime` type decorator, whose
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
that user).
`src/hullbreach_server/auth/deps.py` provides the FastAPI dependency
`get_current_user`, which resolves the `Authorization: Bearer <token>`
header via `resolve_session` and returns an `AuthContext(user, session)`,
raising 401 uniformly for a missing header, an unknown token, an expired
session, or a revoked session (never FastAPI's default 403 on a missing
credential). `require_admin` composes `get_current_user`: it raises 403
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
takes a `RegisterRequest` (`username`, `email` as `EmailStr`, `password`
with `Field(min_length=8)`; `role` is deliberately not a field at all,
never merely ignored) and returns a `UserProfile` (`id`, `username`,
`email`, `role`, `currency`, `rating`, `created_at`) with 201 on success.
`UserProfile.from_user` builds the response from the persisted `User`
row, filling in `currency=0` and the default starting `rating` (1200) --
neither is a real column yet (ELO and currency land in later
milestones). A pre-query (`_duplicate_field`) checks for an existing
`username` or `email` before the insert, so a 409 response can name the
specific offending field (`{"detail": "username already taken",
"field": "username"}` or the `email` equivalent) rather than parsing a
driver `IntegrityError`. A too-short password or malformed email fails
pydantic validation with FastAPI's default 422, no custom body needed.

`POST /api/v1/auth/login` (`src/hullbreach_server/api/auth.py::login`)
takes a `LoginRequest` (`username`, `password`; no `min_length` on
password, shape only) and, on valid credentials, returns a
`LoginResponse` (`token`, `user: UserProfile`) with 200 -- the token
comes from `auth/sessions.py::issue_session` (T-0019). An unknown
username and a wrong password both get the identical 401
`{"detail": "invalid username or password"}`, so the endpoint never
confirms account existence. A failed-login rate limiter guards every
attempt: `is_login_rate_limited`/`record_failed_login`/
`clear_failed_logins` share an in-process `dict[str, deque[datetime]]`
keyed by username (`HULLBREACH_LOGIN_RATE_LIMIT_MAX`/
`_WINDOW_SECONDS`, default 5 attempts / 60 seconds), explicitly
single-instance for 0.1.0 -- it does not survive a process restart or
work across multiple API instances. `current_time()` is the limiter's
one clock read per request, called once in the route and threaded
through both the check and the record call, so a single frozen instant
governs one HTTP request. A successful login calls `clear_failed_logins`
so the next failure does not immediately trip the limit.

`POST /api/v1/auth/logout` (`src/hullbreach_server/api/auth.py::logout`)
requires `Authorization: Bearer <token>` (via `get_current_user`) and
revokes it: `all=false` (the default query param) revokes only the
presented session (`revoke_session`); `all=true` revokes every
non-revoked session for that user (`revoke_all_sessions`, T-0019). 204
No Content on success; 401 (via `get_current_user`) if the token is
already invalid, so logging out twice with the same token 401s the
second time.

`GET /api/v1/auth/session` (`src/hullbreach_server/api/auth.py::session`)
also requires a bearer token and returns a `SessionInfo` (`user_id`,
`role`) with 200 -- deliberately minimal, no `username`/`email`, since
the game server's only need is "who is this and what can they do"
(T-0026). It shares `get_current_user` with `logout`, so a missing,
malformed, expired, or revoked token gets the same uniform 401.

The game client authenticates the same way the browser does: it calls
`POST /api/v1/auth/login` verbatim (no separate route or client-kind
flag -- the design's `f_login_game` flow and `f_login_web` share the
identical `attr "POST /api/v1/auth/login"`), gets back the same
`LoginResponse`, and then presents that token to its own server, which
calls `GET /api/v1/auth/session` server-side to validate it and learn
the player's id and role (T-0026). Neither endpoint distinguishes a
game-client caller from a browser caller; there is nothing in the
request that could, by design.

### Game-server keys

The game server authenticates with a shared secret, not a player session
(T-0052). `AppConfig.game_server_api_keys` is a list of `SecretStr`s, read
from `HULLBREACH_GAME_SERVER_API_KEYS` (comma-separated), the
`[tool.hullbreach_server]` table or a CLI flag like any other field; the
default is empty, and an empty list means no server can authenticate. The
values never appear in a `repr` or in logs. `require_game_server`
(`src/hullbreach_server/auth/server_keys.py`) is the FastAPI dependency a
game-server-only route lists: it reads the `X-Server-Key` header and
answers 401 `{"detail": "not authenticated"}` for a missing, wrong or
unconfigured key (never FastAPI's default 403). The comparison is
`check_server_key`, which returns a typani `Result[None, ServerKeyError]`
(`Missing` or `Invalid`) and compares every configured key with
`hmac.compare_digest` so timing does not reveal a match. No production
route uses the dependency yet; `POST /api/v1/matches` (T-0054) is the first.

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
(T-0037), so a hard delete of a player with matches must fail. The
idempotency key, rating changes and currency payout land with T-0054,
T-0057 and T-0070.

### Database migrations

`hullbreach_server db upgrade` shells out to Alembic (`alembic.ini` at
the repo root, `script_location` pointing at `db/migrations/`) to run
every pending migration up to head; `db seed` calls
`db/seed.py::seed(session)` (T-0008), which idempotently upserts
`db/seed_items.json`'s catalog (120 cosmetic entries across 8
categories, matched by `slug` so a re-run never duplicates a row) into
a hand-declared `items` table (created by the fourth migration below,
T-0101; `seed.py`'s own `Table.create(checkfirst=True)` call is a no-op
wherever that migration has run and exists only for the unit-test
SQLite fixture, which builds its schema from `Base.metadata` rather
than running Alembic), and creates the first admin account
via `auth.passwords.hash_password` when no `User` with `role ==
Role.admin` exists, reading `HULLBREACH_ADMIN_USERNAME`/`_EMAIL`/
`_PASSWORD` and returning `Err(SeedError.MissingAdminPassword)` rather
than inventing one. `db/migrations/env.py::run_migrations_online`
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
`match_player_stats` matching `db/models/match.py` exactly.

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
`text-ink`, `gap-space-8`, `text-font-size-20`, `rounded-radius-8`.

### Routing and page shell

`web/src/router.tsx` builds a `createBrowserRouter` data router: `/` (the
landing content), `/register`, `/login`, `/me` (the profile page), `/me/matches`, `/settings`, and a `*` not-found fallback, all
routed as children of `web/src/App.tsx`'s page shell. `App` renders
`Header`, the routed `Outlet`, and `Footer` -- and stays renderable with no
`Outlet` match (or no router at all) since a bare `<Outlet/>` outside a
router context renders nothing rather than throwing. `web/src/main.tsx`
mounts the tree with `RouterProvider`, not `App` directly.

`web/src/components/Header.tsx` reads `useSession()` (below) and shows
Register/Login links when signed out, or the username and a Log out
control when signed in; every control is a real `<a>`/`<button>` (never a
`<div onClick>`) so tab order and Enter-activation work by construction.
The signed-in Log out control calls `api/auth.ts`'s `logout()` with the
session's token (best-effort: an expired token or a network error does
not block signing out locally), then `clearSession()`, then navigates
home -- `useSession`'s `storage`-event listener means any other open tab
picks up the sign-out too. `web/src/components/Footer.tsx` links to the
cookie and data policy pages.

### Session persistence

`web/src/auth/session.ts` is the client-side session store: a
`StoredSession` (token/userId/username/role) persisted to
`localStorage["hullbreach.session"]`. `saveSession`/`loadSession`/
`clearSession` read and write it directly (`loadSession` guards `JSON.
parse` and returns `null` on anything malformed); `useSession` is the
React hook `Header` and any future consumer read it through -- it
initializes from `loadSession()` synchronously (no signed-out flash on
reload) and re-reads on the `storage` event, so a change in one tab is
reflected in another.

### Auth API client and the register page

`web/src/api/auth.ts` is the one `fetch` wrapper every auth-facing page
uses (docs/design/sprint-1.md sec.5/6): `register`/`login` POST their
request body and resolve to a `UserProfile`/`LoginResponse`; `logout`/
`fetchSession` send a `Bearer` `Authorization` header. Any non-2xx
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
navigates home -- satisfying T-0021's reload-persistence criterion,
since `useSession` reads that same localStorage key back on mount. Any
`ApiError` (401 invalid credentials, 429 rate-limited) sets a
`role="alert"` form-level banner with the server's `detail` message;
Login has no field-level errors (the login contract never names a
`field`).

### Player API client and the profile page

`web/src/api/me.ts` is the client for the signed-in player's own
resources under `/api/v1/me`. It reuses `api/auth.ts`'s `requestJson`
(one `fetch` wrapper, one `ApiError` shape) and `bearerHeaders`. The
`MeResponse` type is the _planned_ contract of `GET /api/v1/me` (T-0031),
which does not exist yet: the `UserProfile` fields (`currency` is the
balance, `rating` the Elo) plus `inventory` (owned skins) and
`recent_matches` (newest first). `MatchSummary` is shared with the match
history (T-0059). The shared fixture `web/tests/fixtures/me.ts` is a typed
instance of that contract, so pages are built and tested before the
endpoint ships.

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

Known gap: the live-server test in `web/tests/unit/Profile.test.tsx` is
`it.fails` until T-0031 lands; when it does, the test passes, `it.fails`
turns red, and that is the cue to drop `.fails`.

### Account settings page

`web/src/pages/Settings.tsx` is routed at `/settings` and edits the
signed-in player's display name (the username), email and password through
`updateMe` in `web/src/api/me.ts`, which is `PATCH /api/v1/me` (planned,
T-0034; the page is built against the fixture
`profileFixture` in `web/tests/fixtures/me.ts`). It copies Register's
inline-error pattern: an `ApiError` with a `field` is shown beside that
input through `aria-describedby`, and one without becomes a `role="alert"`
banner. The planned contract: the request carries only the changed fields,
a new email or password also carries `current_password`, and a wrong one is
a 403 naming `field: "current_password"`. The page enforces the same rule
locally (an email or password change with no current password is refused
inline without a request) and says "Nothing to change." for an untouched
form. On success it clears the secret fields and writes the new username
into the stored session so a reload shows it. Signed out, the page renders
`web/src/components/SignInPrompt.tsx`, the log-in prompt the profile page
now shares.

### Match history page

`web/src/pages/History.tsx` is routed at `/me/matches` and lists the
signed-in player's matches, newest first, through `fetchMatches` in
`web/src/api/me.ts`: `GET /api/v1/me/matches?cursor=` (planned, T-0059;
the page is built against `makeMatchPage` in `web/tests/fixtures/me.ts`).
A `MatchPage` is `{items, next_cursor}`; `next_cursor` is null on the last
page. Each row is `web/src/components/MatchItem.tsx` in `detailed` mode
(opponent, result, rating before and after, date, duration and stats).
Load more requests the next cursor and appends the page; the control is
disabled while a request is in flight, vanishes when the cursor is null,
and after a failed request stays as a retry (labelled Try again if the
first page failed) with the matches already loaded kept. Responses that
belong to an earlier list (StrictMode's double-run effects, a changed
token) are dropped, so no match is listed twice. The page does not
virtualize the list; it relies on the server's page size to keep the DOM
small, and the page size is the server's default (no `limit` is sent).

## Sprint 1 design

`docs/design/sprint-1.md` is the system design for milestone 0.1.0
(database wiring, auth, and the site shell): module map, data model,
config, CLI, auth contracts, web routing, and a per-acceptance-criterion
test plan. `design/hullbreach.strata` is its checked companion model
(nodes, flows, and secrets for the same target architecture).
