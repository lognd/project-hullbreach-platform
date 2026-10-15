+++
id = "01M502JHCDDQQ7WHRG748H1VAK"
title = "Require X-Server-Key on GET /api/v1/auth/session so only real game servers verify sessions"
type = "security"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-15T15:23:28Z"
updated = "2026-10-15T16:02:26Z"
labels = ["owner:lognd", "creates:changelog.d/*.security.md"]
scope = ["src/hullbreach_server/api/auth.py", "src/hullbreach_server/auth/server_keys.py", "tests/unit/test_auth_game.py", "tests/unit/test_server_keys.py", "tests/unit/test_auth_logout.py", "tests/unit/test_me_edit.py", "docs/index.md", "README.md", "docs/design/sprint-1.md", "docs/picking-up-work.md", "web/src/api/auth.ts", "web/tests/unit/Register.test.tsx", ".env.example", "changelog.d/*.security.md"]

[[acceptance]]
text = "GET /api/v1/auth/session called by a game server without a valid X-Server-Key returns 401 not authenticated"
bound = false

[[acceptance]]
text = "The website's own session check keeps working (separate route or documented exemption)"
bound = false

[[acceptance]]
text = "docs/index.md Game-server keys section and README limitations updated"
bound = false
+++

The game repo's platform link (game PR #50, docs/platform-link.md) sends HULLBREACH_PLATFORM_SERVER_KEY as X-Server-Key when its dedicated server verifies a player's bearer token against GET /api/v1/auth/session, and the platform now documents HULLBREACH_GAME_SERVER_API_KEYS in .env.example. But /auth/session does not depend on require_game_server (auth/server_keys.py), so the header is ignored: any caller holding a token can verify it, and a game server with a wrong or missing key is not rejected. Either add a server-only verify route guarded by require_game_server (preferred, so the website keeps using /auth/session with just the bearer token) or guard the existing route for server callers. Note /auth/session also returns no username, so the game shows a client-claimed name; consider returning it from the server-only route. Found while writing the beginner README demo guide.
