# hullbreach_server

The platform API for Project Hullbreach. It owns everything that is not
time-critical: accounts and token sessions, ELO, match history and stats,
the item catalog and cosmetic store, and admin moderation. The game server
reports match results here over REST; the web frontend and the game client
both authenticate against it. Real-time match traffic never touches it.

## Public API

<!-- frob:describes src/hullbreach_server/__main__.py::main -->
<!-- frob:describes src/hullbreach_server/app/app.py::App -->
<!-- frob:describes src/hullbreach_server/app/app.py::create_app -->
<!-- frob:describes src/hullbreach_server/app/config.py::AppConfig -->
<!-- frob:describes src/hullbreach_server/app/config.py::AppConfig.from_external -->
<!-- frob:describes src/hullbreach_server/api/health.py::health -->
<!-- frob:describes src/hullbreach_server/api/health.py::HealthResponse -->
<!-- frob:describes src/hullbreach_server/api/health.py::ready -->
<!-- frob:describes src/hullbreach_server/api/health.py::ReadyResponse -->
<!-- frob:describes src/hullbreach_server/logging/logger.py::get_logger -->
<!-- frob:describes src/hullbreach_server/logging/formatter.py::SimpleFormatter -->
<!-- frob:describes src/hullbreach_server/logging/formatter.py::SimpleFormatter.format -->
<!-- frob:describes src/hullbreach_server/logging/filter.py::BelowLevelFilter -->
<!-- frob:describes src/hullbreach_server/logging/filter.py::BelowLevelFilter.filter -->
<!-- frob:describes src/hullbreach_server/db/engine.py::Base -->
<!-- frob:describes src/hullbreach_server/db/engine.py::DatabaseError -->
<!-- frob:describes src/hullbreach_server/db/engine.py::create_db_engine -->
<!-- frob:describes src/hullbreach_server/db/engine.py::check_connectivity -->
<!-- frob:describes src/hullbreach_server/db/__init__.py::get_engine -->
<!-- frob:describes src/hullbreach_server/db/__init__.py::get_sessionmaker -->
<!-- frob:describes src/hullbreach_server/db/__init__.py::get_db -->
<!-- frob:describes src/hullbreach_server/db/migrations/versions/ba2efc248a9a_baseline_no_tables_yet.py::upgrade -->
<!-- frob:describes src/hullbreach_server/db/migrations/versions/ba2efc248a9a_baseline_no_tables_yet.py::downgrade -->
<!-- frob:describes src/hullbreach_server/db/migrations/versions/0f6d70e4d209_create_users_table.py::upgrade -->
<!-- frob:describes src/hullbreach_server/db/migrations/versions/0f6d70e4d209_create_users_table.py::downgrade -->
<!-- frob:describes src/hullbreach_server/db/models/user.py::Role -->
<!-- frob:describes src/hullbreach_server/db/models/user.py::User -->
<!-- frob:describes src/hullbreach_server/db/seed.py::SeedError -->
<!-- frob:describes src/hullbreach_server/db/seed.py::seed -->
<!-- frob:describes src/hullbreach_server/auth/passwords.py::hash_password -->
<!-- frob:describes src/hullbreach_server/auth/passwords.py::verify_password -->

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

<!-- frob:describes src/hullbreach_server/db/models/session.py::Session -->
<!-- frob:describes src/hullbreach_server/db/models/session.py::_UTCDateTime.process_result_value -->
<!-- frob:describes src/hullbreach_server/auth/sessions.py::SessionError -->
<!-- frob:describes src/hullbreach_server/auth/sessions.py::issue_session -->
<!-- frob:describes src/hullbreach_server/auth/sessions.py::resolve_session -->
<!-- frob:describes src/hullbreach_server/auth/sessions.py::revoke_session -->
<!-- frob:describes src/hullbreach_server/auth/sessions.py::revoke_all_sessions -->
<!-- frob:describes src/hullbreach_server/auth/deps.py::AuthContext -->
<!-- frob:describes src/hullbreach_server/auth/deps.py::get_current_user -->

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
credential).

### Auth API

<!-- frob:describes src/hullbreach_server/auth/schemas.py::RegisterRequest -->
<!-- frob:describes src/hullbreach_server/auth/schemas.py::UserProfile -->
<!-- frob:describes src/hullbreach_server/auth/schemas.py::UserProfile.from_user -->
<!-- frob:describes src/hullbreach_server/api/auth.py::register -->
<!-- frob:describes src/hullbreach_server/auth/schemas.py::LoginRequest -->
<!-- frob:describes src/hullbreach_server/auth/schemas.py::LoginResponse -->
<!-- frob:describes src/hullbreach_server/api/auth.py::login -->
<!-- frob:describes src/hullbreach_server/auth/sessions.py::current_time -->
<!-- frob:describes src/hullbreach_server/auth/sessions.py::is_login_rate_limited -->
<!-- frob:describes src/hullbreach_server/auth/sessions.py::record_failed_login -->
<!-- frob:describes src/hullbreach_server/auth/sessions.py::clear_failed_logins -->
<!-- frob:describes src/hullbreach_server/api/auth.py::logout -->
<!-- frob:describes src/hullbreach_server/api/auth.py::session -->
<!-- frob:describes src/hullbreach_server/auth/schemas.py::SessionInfo -->

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

### Database migrations

<!-- frob:describes src/hullbreach_server/db/migrations/env.py::run_migrations_offline -->
<!-- frob:describes src/hullbreach_server/db/migrations/env.py::run_migrations_online -->
<!-- frob:describes src/hullbreach_server/db/migrations/versions/550676f68926_create_sessions_table.py::upgrade -->
<!-- frob:describes src/hullbreach_server/db/migrations/versions/550676f68926_create_sessions_table.py::downgrade -->
<!-- frob:describes src/hullbreach_server/db/migrations/versions/abbcc4cb6b34_create_items_table.py::upgrade -->
<!-- frob:describes src/hullbreach_server/db/migrations/versions/abbcc4cb6b34_create_items_table.py::downgrade -->

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
diff.

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
landing content), `/register`, `/login`, and a `*` not-found fallback, all
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

## Sprint 1 design

`docs/design/sprint-1.md` is the system design for milestone 0.1.0
(database wiring, auth, and the site shell): module map, data model,
config, CLI, auth contracts, web routing, and a per-acceptance-criterion
test plan. `design/hullbreach.strata` is its checked companion model
(nodes, flows, and secrets for the same target architecture).
