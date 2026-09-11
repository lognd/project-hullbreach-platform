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
<!-- frob:describes src/hullbreach_server/logging/logger.py::get_logger -->
<!-- frob:describes src/hullbreach_server/logging/formatter.py::SimpleFormatter -->
<!-- frob:describes src/hullbreach_server/logging/formatter.py::SimpleFormatter.format -->
<!-- frob:describes src/hullbreach_server/logging/filter.py::BelowLevelFilter -->
<!-- frob:describes src/hullbreach_server/logging/filter.py::BelowLevelFilter.filter -->

`main` parses CLI flags, loads `.env`, builds an `AppConfig`
(pyproject.toml, then `HULLBREACH_*` env vars, then CLI flags), and hands it
to `App`, which runs uvicorn. `create_app` is the pure, socket-free core that
tests exercise through `TestClient`. Routes live in `api/`, one module per
resource, each exposing a `router` that `api_router` mounts under `/api/v1`;
`health` is the liveness probe. The `logging` subpackage provides
`get_logger`, wired per the house logging convention (stdout for DEBUG/INFO,
stderr for WARNING+).

## Web frontend

The React app under `web/` is the player-facing site: landing page, cookie
notice and data policy, registration and login, the profile page, and the
cosmetic store. `web/index.html` is vite's entry; it loads
`web/src/main.tsx`, which mounts `web/src/App.tsx` and imports the
Tailwind stylesheet `web/src/index.css`. In development vite proxies
`/api` to the Python server so the site and the API share an origin.
