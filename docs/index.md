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

`main` parses CLI flags, loads `.env`, builds an `AppConfig`
(pyproject.toml, then `HULLBREACH_*` env vars, then CLI flags), and hands it
to `App`, which runs uvicorn. Running with no subcommand still serves; a
`db` subcommand group (`db upgrade`, `db seed`) instead runs the given
database maintenance step and exits without building `App`/`create_app`.
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

### Database migrations

<!-- frob:describes src/hullbreach_server/db/migrations/env.py::run_migrations_offline -->
<!-- frob:describes src/hullbreach_server/db/migrations/env.py::run_migrations_online -->

`hullbreach_server db upgrade` shells out to Alembic (`alembic.ini` at
the repo root, `script_location` pointing at `db/migrations/`) to run
every pending migration up to head; `db seed` builds on the item catalog
and admin-account loader <!-- frob:until T-0008 -->
that lands in T-0008. `db/migrations/env.py::run_migrations_online`
resolves `HULLBREACH_DATABASE_URL` via `AppConfig` the same way every
other entrypoint does and runs against a caller-supplied connection
(tests) or a fresh engine; `run_migrations_offline` always refuses,
since only online (connected) migrations are supported for 0.1.0
(docs/design/sprint-1.md section 8, open question). Each revision file
under
`db/migrations/versions/` is generated from `script.py.mako`, the
standard Alembic revision template `alembic revision` reads by
convention via `alembic.ini`'s `script_location`. The first revision
(`ba2efc248a9a_baseline_no_tables_yet.py`) is a no-op: its
`upgrade`/`downgrade` create and drop nothing, since no ORM model exists
yet <!-- frob:waive DOC006 reason="planned files per docs/design/sprint-1.md's own module map (section 1) -- named ahead of the tickets that create them, not a claim they exist yet" -->
(`db/models/user.py` is T-0015, `db/models/session.py` is T-0019) -- it
only establishes the revision chain those tickets' own migrations build
on.

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

## Sprint 1 design

`docs/design/sprint-1.md` is the system design for milestone 0.1.0
(database wiring, auth, and the site shell): module map, data model,
config, CLI, auth contracts, web routing, and a per-acceptance-criterion
test plan. `design/hullbreach.strata` is its checked companion model
(nodes, flows, and secrets for the same target architecture).
