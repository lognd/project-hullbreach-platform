# Sprint 1 system design (milestone 0.1.0)

Status: design accepted before implementation. This document is the spec
for T-0006, T-0007, T-0008, T-0010, T-0012, T-0015, T-0016, T-0017, T-0019,
T-0020, T-0021, T-0023, T-0024, T-0026, T-0028, T-0044. Ticket bodies are
thin by design; their acceptance criteria are binding, this document is how
they get satisfied. A test-writing agent should be able to write every
xfail(strict=True) stub from section 7 without asking a question.

Conventions carried over from the existing codebase (do not re-derive):
`AppConfig.from_external` precedence (defaults, then
`[tool.hullbreach_server]`, then `HULLBREACH_*` env, then CLI flags), a
`router` per resource module mounted by `api_router` under `/api/v1`,
module-level `_log = get_logger(__name__)`, pydantic v2 models with
`model_config = {}` (never `class Config`), typani `Result[T, E]` for
fallible internal operations, one-line docstrings on every public symbol,
and `# frob:tests <path>::<symbol> kind="unit"` directly above each public
symbol's test.

## 1. Module map

### Python (`src/hullbreach_server/`)

- `db/__init__.py` -- exports `Base`, `get_engine`, `get_sessionmaker`,
  `get_db` (FastAPI dependency), `DatabaseError`. Owns nothing else; it is
  the package surface other modules import from.
- `db/engine.py` -- owns engine construction: `create_db_engine(url)`
  builds a SQLAlchemy 2.x `Engine` (or `AsyncEngine` -- decision D1, see
  section 8) from `HULLBREACH_DATABASE_URL`, and `check_connectivity(engine)`
  runs `SELECT 1` and returns a typani `Result[None, DatabaseError]`.
  `Base` (the `DeclarativeBase` subclass) lives here so `db/models/*.py`
  and `alembic/env.py` both import it from one place with no cycle back
  to `db/__init__.py`. `db/__init__.py` re-exports it.
- `db/models/user.py` -- the `User` ORM model and the `Role` enum
  (T-0015, T-0028).
- `db/models/session.py` -- the `Session` ORM model (T-0019).
- `db/migrations/` -- an Alembic environment: `alembic.ini` lives at the
  package root of this folder is not possible (Alembic wants its ini next
  to the script location or referenced by path), so the layout is:
  - `db/migrations/env.py` -- imports `Base` and every model module from
    `db/models/` so `Base.metadata` is fully populated, reads
    `HULLBREACH_DATABASE_URL` the same way `AppConfig` does (env var
    first, falling back to the config's default) rather than hardcoding
    a URL, and runs in "online" mode only (no offline SQL generation
    needed for 0.1.0 -- recorded as an open question in section 8).
  - `db/migrations/script.py.mako` -- the standard Alembic template.
  - `db/migrations/versions/` -- one revision file per migration; the
    first revision creates `users`; a second (from T-0019) adds
    `sessions`; a third (from T-0008's seed, see section 4) adds the
    minimal `items` table.
  - `alembic.ini` at the repo root (sibling to `pyproject.toml`), pointing
    `script_location = src/hullbreach_server/db/migrations`. This file is
    outside every ticket's declared `scope`; T-0007 adds it under the
    `pyproject.toml`/config-file exception the brief allows ("dependency
    additions and config wiring... allowed when the ticket needs them"),
    or files a scope-add if the gate objects.
- `db/seed.py` -- `seed(session) -> Result[SeedReport, DatabaseError]`:
  idempotent load of `db/seed_items.json` into the `items` table and
  creation of exactly one admin account if none exists (T-0008).
- `db/seed_items.json` -- static catalog data, >= 100 entries, each
  `{"slug": str, "name": str, "price": int}` (slug is the natural key
  seed uses for idempotency).
- `auth/passwords.py` -- `hash_password(plain) -> str`,
  `verify_password(plain, hashed) -> bool` (T-0015).
- `auth/sessions.py` -- `issue_session(db, user) -> tuple[Session, str]`
  (returns the ORM row and the one-time plaintext token),
  `hash_token(token) -> str`, `resolve_session(db, token) ->
  Result[Session, SessionError]` checking expiry and revocation, and
  `revoke_session` / `revoke_all_sessions` (T-0019, used by T-0023).
- `auth/deps.py` -- FastAPI dependencies: `get_current_user` (401 on
  missing/invalid/expired/revoked token) and `require_admin` (403 if the
  resolved user's role is not `admin`) (T-0019, T-0028).
- `auth/schemas.py` -- pydantic request/response models for register,
  login, session, and the profile view. `role` is never an input field
  and never appears in any response schema that a non-admin caller sees
  (T-0016, T-0028).
- `api/auth.py` -- `router` with `/register`, `/login`, `/logout`,
  `/session` (T-0016, T-0020, T-0023, T-0026).
- `api/health.py` -- gains `/ready` alongside the existing `/health`
  (T-0012); no new file, existing scope.
- `__main__.py` -- gains `db` subparser with `upgrade` and `seed`
  subcommands (T-0007, T-0008); existing scope, additive only.

### Web (`web/src/`)

- `router.tsx` -- route table: `/` (landing, existing `App.tsx` content
  moves under a route), `/register`, `/login`, and a catch-all. Built on
  `react-router-dom` (added to `package.json` under the same
  dependency-addition exception as above).
- `App.tsx` -- becomes the page shell: renders `Header`, an `<Outlet />`
  (or the router's children), and `Footer`. No longer the landing page
  body itself.
- `components/Header.tsx` -- shows the brand, nav, and either
  Register/Login links (signed-out) or the username and a Logout control
  (signed-in) (T-0044, T-0024).
- `components/Footer.tsx` -- static links (cookie notice, data policy
  placeholders); no signed-in/out branching needed in 0.1.0.
- `pages/Register.tsx`, `pages/Login.tsx` -- forms with inline,
  field-scoped validation error display (T-0017, T-0021).
- `api/auth.ts` -- `register`, `login`, `logout`, `fetchSession` thin
  wrappers over `fetch`, typed against the same shapes as
  `auth/schemas.py` (mirrored by hand; there is no codegen step in
  0.1.0 -- open question, section 8).
- `auth/session.ts` -- reads/writes the persisted session
  (`localStorage` key `hullbreach.session`), and a small subscriber
  hook (`useSession`) so `Header` re-renders on login/logout without a
  full page reload (T-0021).

## 2. Data model

SQLAlchemy 2.x declarative style (`Mapped[...]` / `mapped_column`), engine
in `db/engine.py`:

```python
class Base(DeclarativeBase):
    """Shared declarative base for every ORM model; owns Alembic's naming convention."""
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })
```

The naming convention is set once on `Base.metadata` so every migration
Alembic autogenerates gets a deterministic constraint name -- without it,
unnamed constraints get driver-assigned names that differ run to run and
autogenerate produces spurious diffs.

### `User` (`db/models/user.py`, table `users`)

| column         | type                          | constraints                          |
|----------------|-------------------------------|---------------------------------------|
| id             | UUID (default `uuid4`)        | primary key                           |
| username       | String(32)                    | not null, unique (`uq_users_username`)|
| email          | String(254)                   | not null, unique (`uq_users_email`)   |
| password_hash  | String(255)                   | not null                              |
| role           | Enum(`Role`), native_enum=False, values_callable | not null, default `player` |
| created_at     | DateTime(timezone=True)       | not null, server_default `now()`      |

`Role` is a `str, enum.Enum` with members `player` and `admin`.
`native_enum=False` stores it as a `VARCHAR` with a `CHECK` constraint
(`ck_users_role`) rather than a Postgres native enum type, so adding a
role later (a plain data migration) never requires `ALTER TYPE`.

Suspension fields (`suspended_at`, `suspended_reason`) are explicitly
deferred past 0.1.0 -- noted here so nobody adds them speculatively; file
a new ticket when moderation lands.

Indexes: the two unique constraints above double as lookup indexes
(username at login, email at registration). No separate index needed.

### `Session` (`db/models/session.py`, table `sessions`)

| column      | type                     | constraints                                          |
|-------------|--------------------------|-------------------------------------------------------|
| id          | UUID (default `uuid4`)   | primary key                                            |
| user_id     | UUID                     | not null, FK `users.id` `ON DELETE CASCADE`, indexed (`ix_sessions_user_id`) |
| token_hash  | String(64)               | not null, unique (`uq_sessions_token_hash`)            |
| created_at  | DateTime(timezone=True)  | not null, server_default `now()`                       |
| expires_at  | DateTime(timezone=True)  | not null                                               |
| revoked_at  | DateTime(timezone=True)  | nullable                                               |

The plaintext token is never stored; `token_hash` is `sha256(token)`
hex-encoded (64 chars), looked up by exact match on login-protected
routes so no plaintext token round-trips into the database. A session is
valid iff `revoked_at is None and expires_at > now()`; `resolve_session`
checks both in one query rather than two round trips.

Both models import `Base` from `hullbreach_server.db.engine` (re-exported
by `hullbreach_server.db`), never redefine it -- this is the reason `Base`
lives in `engine.py` rather than in each model module: T-0006 lands before
the models exist, so the base needs a home that does not depend on them.

## 3. Config

New `AppConfig` fields (T-0006), added to the existing model in
`app/config.py` (already-declared scope for that file is owned by T-0005's
parent story; T-0006's own scope only touches `db/`, so `AppConfig` itself
is not edited by T-0006 -- see decision D2 in section 8 for how the engine
still gets a URL without touching `app/config.py`).

- `HULLBREACH_DATABASE_URL` -- already exists as `AppConfig.database_url`
  (see `config.py` today); T-0006 reads it via `AppConfig.from_external()`
  called the same way `__main__.py` already does, not via a second
  ad-hoc `os.environ.get`.
- `HULLBREACH_SESSION_TTL_SECONDS` (new, default `1209600` = 14 days) --
  read directly by `auth/sessions.py` with `os.environ.get`, following the
  same `HULLBREACH_` prefix convention as `AppConfig`, since it is
  auth-specific rather than a wiring concern (documented in `.env.example`
  next to the existing keys).
- `HULLBREACH_LOGIN_RATE_LIMIT_MAX` (new, default `5`) and
  `HULLBREACH_LOGIN_RATE_LIMIT_WINDOW_SECONDS` (new, default `60`) --
  read by `auth/sessions.py`'s rate limiter (section 5).

### Fail-fast startup (T-0006)

`create_db_engine(url)` builds the engine lazily (SQLAlchemy engines do
not open a connection until first use), so "fail fast at startup" means
`App.__call__` (or a startup hook -- decision D2) calls
`check_connectivity(engine)` before calling `uvicorn.run` and exits
non-zero on failure, logging at `ERROR`:

```
Cannot reach database at <host>:<port> (database=<name>): <driver error>
```

`<host>` is parsed out of the URL with `sqlalchemy.engine.make_url(url)`
so the message never depends on string-splitting; this is also exactly
what acceptance criterion 1 on T-0006 requires ("a message naming the
host"). The full URL (with any embedded password) is never logged --
only `.host`, `.port`, and `.database` from the parsed `URL` object.

### Readiness endpoint (T-0012)

`GET /api/v1/ready` in the existing `api/health.py`:

- 200, body `{"status": "ready", "database": "ok"}` when
  `check_connectivity` succeeds.
- 503, body `{"status": "not_ready", "database": "unreachable"}` when it
  does not. The route catches the `Result`'s `Err` and never raises past
  FastAPI -- a `Response(status_code=503, ...)` returned directly, since
  `response_model` on success and a different shape on failure do not mix
  cleanly with FastAPI's default single `response_model` decorator
  argument (call `JSONResponse` explicitly on the 503 path instead).
- `/health` (liveness) is unchanged: it still never touches the database.

## 4. CLI

`__main__.py` gains one subparser group, composed with the existing
top-level `--host`/`--port` flags rather than replacing them: running
`hullbreach_server` with no subcommand still serves, exactly as today.

```python
sub = p.add_subparsers(dest="command")
db_p = sub.add_parser("db", help="database maintenance")
db_sub = db_p.add_subparsers(dest="db_command", required=True)
db_sub.add_parser("upgrade", help="run pending Alembic migrations")
db_sub.add_parser("seed", help="load catalog items and the first admin")
```

`main()` branches: if `args.command == "db"`, dispatch to
`db upgrade` (shells out to `alembic.config.main(["-c", "alembic.ini",
"upgrade", "head"])`, matching the acceptance criterion "alembic heads
match the models") or `db seed` (builds an engine from `AppConfig`, opens
a session, calls `seed()`) and exits without starting uvicorn. Neither
subcommand builds `App`/`create_app`.

T-0007's acceptance criterion is verified by an Alembic
`autogenerate --check`-style comparison in `tests/system/test_build.py`:
build the engine against a throwaway SQLite database, run `upgrade head`,
then assert `alembic.autogenerate.compare_metadata` against `Base.metadata`
returns no diffs.

### Seed idempotency and the items problem (T-0008)

<!-- frob:until T-0066 -->
T-0066 (Item model, milestone 0.3.0) does not exist yet, so `db/seed.py`
cannot seed rows into a model owned by a future ticket. Decision (see D3
in section 8): T-0007's first migration set includes a **minimal**
`items` table -- `id (UUID pk)`, `slug (String(64), unique)`,
`name (String(120))`, `price_cents (Integer)` -- owned by the migration,
with no ORM model in `db/models/` yet (seed writes it with a raw
`sqlalchemy.Table` reflected or hand-declared in `seed.py`, not a mapped
class, so nothing outside `db/seed.py`/`db/migrations` depends on its
shape). T-0066 later either reuses this table (adding a proper ORM model
over the same columns, migrating additively) or supersedes it with an
explicit migration; either way is that ticket's decision to make, not
this one's.

Idempotency: `seed()` upserts each catalog row by `slug` (`INSERT ...
ON CONFLICT (slug) DO NOTHING` via SQLAlchemy's
`postgresql.insert(...).on_conflict_do_nothing()`, with a portable
fallback for SQLite tests using `sqlite.insert(...).on_conflict_do_nothing()`
-- both dialects support the same `on_conflict_do_nothing` API surface in
SQLAlchemy 2.x, so `seed.py` picks the insert constructor from
`session.bind.dialect.name` rather than hardcoding one dialect), and
creates the admin only when no `User` row has `role == Role.admin` yet
(a second run must not create a second admin or error). The admin's
username/email/password come from `HULLBREACH_ADMIN_USERNAME`,
`HULLBREACH_ADMIN_EMAIL`, `HULLBREACH_ADMIN_PASSWORD` env vars (documented
in `.env.example` with placeholder values); `seed()` returns an `Err` if
`HULLBREACH_ADMIN_PASSWORD` is unset and no admin exists yet, rather than
inventing or logging a password.

## 5. Auth

### Password hashing (T-0015)

Decision (D4, section 8): `pwdlib[argon2]`, not `passlib`. `passlib` is in
maintenance mode with no active release addressing newer Python versions;
`pwdlib` is the maintained successor with the same `PasswordHash`
interface and Argon2id as its default scheme. Added to `pyproject.toml`
dependencies via `uv add "pwdlib[argon2]"`.

```python
_hasher = PasswordHash.recommended()  # Argon2id

def hash_password(plain: str) -> str:
    """Hash a plaintext password with Argon2id; the result is safe to store."""
    return _hasher.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against a stored Argon2id hash."""
    return _hasher.verify(plain, hashed)
```

### Token format (T-0019, T-0020, T-0026)

Opaque bearer token: `secrets.token_urlsafe(32)` (256 bits), returned to
the caller exactly once (register does not log a caller in automatically
-- login does). At rest, only `sha256(token).hexdigest()` is stored in
`sessions.token_hash`; a lookup hashes the presented token and does an
equality match (no timing-sensitive comparison needed beyond what a
unique-index lookup already gives, since the hash itself is the
comparison key, not a raw string compare against a secret). Session TTL
is `HULLBREACH_SESSION_TTL_SECONDS` (default 14 days), set at issuance as
`expires_at = now() + timedelta(seconds=ttl)`.

### Endpoints (`api/auth.py`)

All four share the pattern: pydantic request model, pydantic response
model, `Depends(get_db)` for a `Session` (SQLAlchemy) from `db.get_db`.
`role` never appears as an input field on any schema and never appears in
any response schema returned to the caller whose own role it is not
(profile/session responses expose `role` only for the caller's own
account, since the game server and the caller itself both legitimately
need to know it -- an admin route listing *other* users, not in scope for
0.1.0, would need to gate that separately).

**POST /api/v1/auth/register**
- Request `RegisterRequest {username: str, email: EmailStr, password: str}`
  (pydantic `EmailStr`, already fine per pydantic v2 conventions;
  `password` min length 8, enforced with a pydantic `Field(min_length=8)`
  plus a `field_validator` if more than length is required -- 0.1.0
  requires only length).
- Response `UserProfile {id: UUID, username: str, email: str, role: Role,
  currency: int, rating: int, created_at: datetime}`. `currency` and
  `rating` are not yet backed by real columns (ELO/currency land in later
  tickets outside this sprint); T-0016's acceptance criterion says "role
  Player, currency 0, rating default" so `UserProfile` returns literal
  `currency=0` and a `rating` default constant (`1200`, standard ELO
  starting value) hardcoded in the response builder for 0.1.0, not
  persisted columns -- documented here so nobody is surprised these two
  fields do not round-trip through the database yet.
- 201 with `UserProfile` on success.
- 409 on duplicate username OR email:
  `{"detail": "username already taken", "field": "username"}` or the
  `email` equivalent -- checked with a pre-query (`SELECT 1 WHERE
  username = :u OR email = :e`) so the specific field is knowable before
  the insert, rather than parsing a driver `IntegrityError`.
- 422 (FastAPI's default) for schema-level validation failures (e.g.
  password too short, malformed email) -- no custom body needed there.

**POST /api/v1/auth/login**

<!-- frob:until T-0020 -->
- Request `LoginRequest {username: str, password: str}`.
- Response `LoginResponse {token: str, user: UserProfile}`, 200.
- 401 `{"detail": "invalid username or password"}` on bad credentials --
  deliberately identical whether the username does not exist or the
  password is wrong, so the endpoint never confirms account existence.
- 429 `{"detail": "too many attempts, try again later"}` after 5 failed
  attempts within a 60-second window for the same username (config
  values from section 3). Store: an in-process
  `dict[str, deque[datetime]]` behind a module-level lock in
  `auth/sessions.py` (`_failed_attempts`), explicitly acceptable for
  0.1.0 per the brief (no Redis dependency yet); a successful login
  clears that username's deque. This does not survive a process restart
  or work across multiple API instances -- noted as an open question in
  section 8 for when the platform runs more than one instance.

**POST /api/v1/auth/logout**
- No request body. Requires `Authorization: Bearer <token>` (via
  `get_current_user`, which also resolves the `Session` row, not just the
  `User`, for this route specifically -- `get_current_user` returns both
  via a small `AuthContext(user, session)` so `logout` does not need a
  second lookup).
- Query param `all: bool = False`. `all=false` revokes only the
  presented session (`revoke_session`); `all=true` revokes every
  non-revoked session for that user (`revoke_all_sessions`).
- 204 No Content on success. 401 if the token is already invalid (same
  path as any other protected route).

**GET /api/v1/auth/session**
- Requires `Authorization: Bearer <token>`, used by the game server to
  validate a client-presented token server-side.
- Response `SessionInfo {user_id: UUID, role: Role}`, 200. Deliberately
  minimal -- no username/email, since the game server's only need is
  "who is this and what can they do."
- 401 on missing/invalid/expired/revoked token, same shape as other
  protected routes: `{"detail": "not authenticated"}`.

### `get_current_user` / `require_admin` (T-0019, T-0028)

Both are FastAPI dependencies in `auth/deps.py`:

```python
async def get_current_user(
    token: str = Depends(_bearer_scheme), db: DBSession = Depends(get_db)
) -> AuthContext:
    """Resolve the bearer token to its session and user, or raise 401."""
```

using `fastapi.security.HTTPBearer` for `_bearer_scheme` so a missing
header is itself a 403 from FastAPI's security layer today -- normalized
to 401 by setting `HTTPBearer(auto_error=False)` and raising
`HTTPException(401, "not authenticated")` explicitly when the credential
is absent or `resolve_session` returns `Err`, so every failure mode on
this dependency is uniformly 401 regardless of *why* (missing header,
malformed token, expired, revoked -- all 401, never 403).

`require_admin` composes `get_current_user`:

```python
async def require_admin(ctx: AuthContext = Depends(get_current_user)) -> AuthContext:
    """Require the resolved caller to hold the admin role, or raise 403."""
    if ctx.user.role is not Role.admin:
        raise HTTPException(403, {"detail": "admin role required"})
    return ctx
```

401 means "I don't know who you are"; 403 means "I know who you are and
the answer is no" -- this is why `require_admin` is a second dependency
layered on `get_current_user` rather than one dependency with a role
parameter, matching T-0028's acceptance criterion exactly (403 with a
permissions message for a Player token on an admin route).

## 6. Web

### Routes (`router.tsx`)

```
/            -> landing (current App.tsx body, moved to pages/Landing.tsx)
/register    -> pages/Register.tsx
/login       -> pages/Login.tsx
*            -> simple not-found page
```

`App.tsx` renders `<Header /><Outlet /><Footer />`; `main.tsx` wraps it in
`<BrowserRouter>` from `router.tsx`'s exported `router` (using
`createBrowserRouter`/`RouterProvider`, the currently-recommended
react-router-dom v6 data API, not the older `<Routes>` JSX form, so route
loaders are available to later tickets without a rewrite).

### Header / Footer signed-in vs signed-out (T-0044, T-0024)

`Header` reads `useSession()` from `auth/session.ts`. Signed-out: brand
plus "Register" and "Login" links. Signed-in: brand plus the username and
a "Log out" button. The button calls `api/auth.ts`'s `logout()`, then
`session.ts`'s `clearSession()`, then navigates to `/` -- matching
T-0024's acceptance criterion exactly (session cleared, landing page
shown). Every interactive element in `Header` is a real `<a>`/`<button>`
(never a `<div onClick>`), which is what makes T-0044's tab-order/Enter
acceptance criterion true by construction rather than by a later ARIA
patch.

### Session persistence (T-0021)

`auth/session.ts`:

```ts
export type StoredSession = { token: string; userId: string; username: string; role: string };

export function saveSession(s: StoredSession): void   // writes localStorage["hullbreach.session"]
export function loadSession(): StoredSession | null    // reads it back, JSON.parse guarded by try/catch
export function clearSession(): void                   // removes the key
export function useSession(): StoredSession | null      // React hook: state + storage-event listener
```

`useSession` initializes its state from `loadSession()` synchronously (no
flash of signed-out state on reload) and subscribes to the `storage`
event so a logout in one tab reflects in another -- this is also how
`Header` "just re-renders" without prop drilling from `Login`/`Register`.
On mount, `Login.tsx`'s success handler calls `saveSession(...)` with the
`LoginResponse` from `api/auth.ts`, satisfying T-0021's reload criterion.

### Forms with inline validation errors (T-0017, T-0021)

Both `Register.tsx` and `Login.tsx` keep a `fieldErrors: Record<string,
string>` state. On submit, `api/auth.ts` throws a typed `ApiError {status:
number, detail: string, field?: string}` when the response is not ok;
the catch block sets `fieldErrors[field] = detail` when `field` is
present (409 on register, e.g. `{field: "username"}`) and a
form-level error banner otherwise (401 on login, 429 on login). Each
input renders its own error directly beneath it, keyed by `name`, which
is what T-0017's acceptance criterion requires ("shown next to the
field") and what `Register.test.tsx` asserts against
(`getByLabelText("Username").nextSibling` or an
`aria-describedby`-linked error element -- decision: use
`aria-describedby` pointing at a `<p id="{field}-error">`, both for
accessibility and because it gives the test a stable query target via
`getByText` scoped near the input).

## 7. Test strategy

Unit tests use SQLite through a URL override: a `conftest.py` fixture
(`tests/unit/conftest.py`, new file, in scope for whichever ticket first
needs it -- T-0006's `tests/unit/test_db_engine.py` is scope-eligible to
add it since fixtures shared across `tests/unit/` conventionally live
there) provides:

- `engine` -- `create_db_engine("sqlite:///:memory:")` with
  `StaticPool` and `connect_args={"check_same_thread": False}` so the
  same in-memory database is visible across the connections FastAPI's
  `TestClient` and the test itself both open.
- `db_session` -- runs `Base.metadata.create_all(engine)`, yields a
  `sqlalchemy.orm.Session`, rolls back and drops all tables after.
- `app` / `client` -- `create_app(AppConfig(database_url="sqlite://"))`
  with `app.dependency_overrides[get_db]` pointed at the `db_session`
  fixture, wrapped in `TestClient`, matching the existing
  `create_app`-is-pure convention (no real engine touches a socket in
  unit tests).

No live-Postgres test exists in 0.1.0; `tests/system/test_build.py`'s
Alembic check (section 4) also runs against the SQLite/in-memory engine,
which Alembic supports for DDL-only migrations (no Postgres-only column
types are used in the three 0.1.0 migrations, so this holds).

Every row below is a planned `xfail(strict=True)` stub for the next step,
one node id per acceptance criterion, in the ticket's own scoped test
file:

| Ticket | Acceptance criterion | Planned test node id |
|--------|----------------------|------------------------|
| T-0006 | unreachable URL fails startup naming the host | `tests/unit/test_db_engine.py::test_check_connectivity_names_host_on_unreachable_url` |
| T-0007 | upgrade head matches models | `tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata` |
| T-0008 | seed reaches >=100 items and one admin | `tests/unit/test_seed.py::test_seed_creates_100_items_and_one_admin` |
| T-0008 | re-running seed does not duplicate | `tests/unit/test_seed.py::test_seed_is_idempotent_on_second_run` |
| T-0010 | green CI without approval is blocked | (process control, not a code test -- verified by a documented manual check in CONTRIBUTING.md; no test node id) |
| T-0012 | ready is 200 when reachable, 503 when not | `tests/unit/test_api.py::test_ready_returns_200_when_database_reachable` and `tests/unit/test_api.py::test_ready_returns_503_when_database_unreachable` |
| T-0015 | hash then verify succeeds, stored value is not the password | `tests/unit/test_passwords.py::test_hash_password_verifies_and_does_not_store_plaintext` |
| T-0016 | duplicate username gets 409 with field-specific message | `tests/unit/test_auth_register.py::test_register_duplicate_username_returns_409_with_field` |
| T-0016 | valid request gets 201, role Player, currency 0, rating default | `tests/unit/test_auth_register.py::test_register_valid_request_returns_201_with_player_defaults` |
| T-0017 | field error is shown next to the field | `web/tests/unit/Register.test.tsx::shows field error next to the offending input` |
| T-0019 | expired or revoked token gets 401 on protected route | `tests/unit/test_sessions.py::test_expired_token_returns_401` and `tests/unit/test_sessions.py::test_revoked_token_returns_401` |
| T-0020 | sixth failed attempt in a minute gets 429 | `tests/unit/test_auth_login.py::test_sixth_failed_login_attempt_in_window_returns_429` |
| T-0021 | session persists across reload | `web/tests/unit/Login.test.tsx::keeps user signed in after reload` |
| T-0023 | token rejected after logout | `tests/unit/test_auth_logout.py::test_logout_revokes_token_so_it_is_rejected_afterward` |
| T-0024 | logout clears session and shows landing page | `web/tests/unit/Header.test.tsx::clears session and navigates home on logout click` |
| T-0026 | game server session lookup returns player id and role | `tests/unit/test_auth_game.py::test_session_endpoint_returns_player_id_and_role_for_valid_token` |
| T-0028 | Player token on admin route gets 403 with permissions message | `tests/unit/test_roles.py::test_player_token_on_admin_route_returns_403_with_permissions_message` |
| T-0044 | tab order matches visual order, Enter activates every control | `web/tests/unit/Header.test.tsx::tab order matches visual order and Enter activates each control` |

## 8. Open questions and decisions made

- **D1 -- sync vs async SQLAlchemy engine.** Decision: sync
  (`sqlalchemy.create_engine`, `psycopg[binary]` as the driver, not
  `asyncpg`). Reason: `create_app` and every route in `api/health.py`
  today are sync `def`, FastAPI runs sync routes in a threadpool without
  penalty at this traffic scale, and a sync engine keeps `db/engine.py`
  and every dependency in `auth/deps.py` free of an async/await split
  that buys nothing until the platform has real concurrency pressure --
  revisit only if profiling says otherwise.
- **D2 -- where fail-fast startup is invoked without T-0006 touching
  `app/config.py` or `app/app.py` (both outside T-0006's declared
  scope).** Decision: `db/engine.py` exposes
  `create_db_engine_from_config(cfg: AppConfig) -> Engine` plus
  `check_connectivity`, and T-0006 itself only adds a unit test proving
  `check_connectivity` fails correctly (its acceptance criterion is about
  the *behavior* of the check, not about `App` calling it yet). Wiring
  `App.__call__` to call `check_connectivity` before `uvicorn.run` is
  `app/app.py`, out of T-0006's scope -- filed as a follow-up scope note
  rather than silently expanded: the ticket that actually wires it
  (whichever of T-0005's children touches `app/app.py`) does that call
  and its own test; T-0006 provides the function and waives WIRE001 with
  `follow_up` naming that ticket once it exists. If no such ticket exists
  yet when T-0006 is implemented, file one (`kind=feature`, scope
  `src/hullbreach_server/app/app.py`, `tests/unit/test_app.py`) rather
  than leaving the function permanently unwired.
- **D3 -- how T-0008 seeds items without the T-0066 Item model.**
  Decision: a minimal, migration-owned `items` table with no ORM model
  yet (section 4). Reason: waiting for T-0066 would block sprint-1's
  acceptance criteria (>=100 items seeded) on a 0.3.0 ticket; a
  hand-declared `sqlalchemy.Table` confines the temporary shape to
  `db/seed.py` and one migration file, so T-0066 has a clean, additive
  path (either adopt the same table or migrate it) instead of a second
  parallel items concept to reconcile later.
- **D4 -- password hashing library.** Decision: `pwdlib[argon2]` over
  `passlib` (section 5). Reason: passlib's last release predates modern
  Python packaging and it is unmaintained; pwdlib is the documented
  successor with an equivalent API and Argon2id by default.
- **Open, not decided here -- rate limiter across multiple API
  instances.** The in-process failed-login store (section 5) is correct
  for a single instance, which is what 0.1.0 deploys. If sprint 2 or
  later runs more than one API process behind a load balancer, the
  limiter needs a shared store (Redis, or the database itself); tracked
  as a note for whoever files that ticket, not solved speculatively now.
- **Open, not decided here -- web/API schema drift.** `api/auth.ts`'s
  request/response shapes are hand-mirrored from `auth/schemas.py` with
  no codegen in 0.1.0. This is an accepted manual-sync cost for this
  sprint; an OpenAPI-client-generation step (FastAPI already serves
  `/api/openapi.json`) is a reasonable later addition but out of scope
  here.
- **Open, not decided here -- Alembic offline mode.** `db/migrations/env.py`
  only implements online (connected) migration runs for 0.1.0, since
  `hullbreach_server db upgrade` always has a live connection available.
  Offline SQL-script generation (`alembic upgrade --sql`) is not
  implemented; add it if a deployment process later needs a
  DBA-reviewed SQL diff instead of a live migration run.

## 9. strata model (`design/hullbreach.strata`)

The kernel-checked companion to this document: nodes for the browser
(untrusted), the game client and game server (external, `managed`), the
platform API split by planned package (`api`, `app`, `auth`, `db`,
`logging`, `root`, matching section 1's module map), and the Postgres
database (`managed`, external infrastructure); flows for every HTTP call
in section 5 plus the internal API-to-auth, auth-to-db, and db-to-Postgres
hops; and three `secret` declarations (`session_token`, `password_hash`,
`database_url`) per `docs/strata/surface.md`'s `std.secrets`
cache-of-authority model, each with `issued_by`, `audience`, `lifetime`,
and a mandatory `revoke` bound.

`frob check --only sys` and `frob sys audit` were run against this branch
and did **not** come back clean; the full six-phase `boundary` construct
from `docs/strata/boundary.md` (admit/parse/judge/effect/record/refuse,
plus `operation`/`atomic` framing) was judged infeasible to model
correctly in the time available for a design-only pass with no code yet
to bind it to, so no `boundary Ingress between browser and
hullbreach_server_api { ... }` block exists in the file -- this is the
one deliberately-omitted piece the brief asked to be named precisely.
Everything else attempted (nodes, flows, secrets, `may` capability grants
for the three effects already observed in the existing `app`/`root`
code) is in the file. Findings left as named, undischarged assumptions
rather than fixed, because fixing them either requires code that does not
exist yet (T-0006 etc. have not landed) or requires machinery (a real
ticket, a `frob:doc`/`frob:tests` edge into a design file with no test
suite of its own yet) that postdates this design step:

- **SCOPE001 / PRE001** -- this branch (`docs/sprint-1-design`) is not
  named `T-####-*` and no single ticket covers "write the design," so
  frob's scope/pre-work gate cannot derive an active ticket for the diff.
  Assumption: acceptable for a docs/design-only PR with no ticket of its
  own, per the coordinator's explicit instruction to produce this
  document before any implementation ticket exists; revisit if the team
  wants a dedicated `T-####` tracking ticket for "sprint-1 design" itself.
- **COV002** (every new node/flow in `design/hullbreach.strata` has no
  `frob:ticket` edge) -- each construct in the model corresponds to a
  ticket named in section 1-7 above (T-0006, T-0007, T-0015, T-0016,
  T-0019, T-0020, T-0023, T-0026, T-0044, etc.) but the model was written
  before those tickets' own branches exist to carry a `frob:ticket`
  comment; the mapping lives in this document's tables instead of inline
  directives. Assumption: the implementing agent for each ticket adds the
  `frob:ticket T-XXXX` directive to its node/flow lines in
  `design/hullbreach.strata` as part of that ticket's own change, at
  which point COV002 clears for that construct.
- **SYS002** (every declared `secret` has no code binding / enforcing
  site) -- none of `auth/sessions.py`, `auth/passwords.py`, or the engine
  module exist yet on this branch. Assumption: the ticket that
  implements each secret's enforcement point (`auth/sessions.py` for
  `session_token`, `auth/passwords.py` for `password_hash`,
  `db/engine.py` for `database_url`) adds the `frob:secret <name>`
  directive at the real call site once it lands.
- **TEST009** (`design/hullbreach.strata` has no e2e test bound) -- no
  end-to-end test harness exercising the full auth flow exists yet in
  0.1.0. Assumption: deferred until an end-to-end test is written
  against the real endpoints (candidate: a `tests/system/` case once
  T-0016/T-0020/T-0023 all land), tracked here rather than invented as a
  placeholder test with nothing to assert.
- **COV001** on `web/src/App.tsx` and the four internal flows
  (`f_api_to_auth`, `f_auth_to_db`, `f_api_to_db`, `f_db_to_postgres`) --
  missing `frob:doc` anchors. Assumption: added by whichever ticket's
  change first touches each of those lines, the same as COV002 above,
  rather than backfilling anchors into a document with no corresponding
  code section yet.

None of the above were waived with `frob:waive` inside `design/
hullbreach.strata` itself, since waiving implies "this will not be fixed
by design," which is false here -- each is fixed by a specific,
already-named future ticket. They are recorded here, in this document's
own open-questions section, as the brief asked for.
