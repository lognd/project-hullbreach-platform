+++
id = "01M4GS9A33TBP96SJ646TZCHZ0"
title = "Issue session as HttpOnly cookie so web can restore sessions after reload"
type = "security"
category = "todo"
priority = "low"
reporter = "a-carten"
created = "2026-10-09T16:52:32Z"
updated = "2026-10-26T09:40:12Z"
labels = ["owner:lognd", "creates:src/hullbreach_server/auth/cookies.py", "creates:tests/unit/test_auth_cookie.py", "creates:web/tests/unit/SessionRestore.test.tsx", "creates:changelog.d/01M4GS9A33TBP96SJ646TZCHZ0.changed.md"]
scope = ["src/hullbreach_server/api/auth.py", "src/hullbreach_server/auth/deps.py", "src/hullbreach_server/auth/__init__.py", "src/hullbreach_server/app/app.py", "web/src/auth/session.ts", "web/src/main.tsx", "web/src/components/Header.tsx", "web/src/api/auth.ts", "docs/index.md", "docs/demo-runbook.md", "invariants/INV-006.md", "src/hullbreach_server/auth/cookies.py", "tests/unit/test_auth_cookie.py", "web/tests/unit/SessionRestore.test.tsx", "changelog.d/01M4GS9A33TBP96SJ646TZCHZ0.changed.md", "web/tests/unit/Leaderboard.test.tsx", "tests/unit/test_leaderboard.py", "web/src/api/me.ts"]

[[links]]
kind = "discovered-from"
target = "01M4GR6ES87DSS119XV7PR4BF7"

[[acceptance]]
text = "given valid credentials, when logging in, then the response sets an HttpOnly SameSite session cookie and still returns the bearer token for the game client"
bound = true

[[acceptance]]
text = "given only the session cookie, when calling GET /api/v1/me, then the caller is authenticated; given the cookie on a state-changing request without the CSRF header, then it is refused 403"
bound = true

[[acceptance]]
text = "given a cookie session, when logging out, then the session is revoked and the cookie cleared"
bound = false

[[acceptance]]
text = "given a signed-in web user, when the page reloads, then the session is restored from the cookie via GET /api/v1/me and no token is in script-readable storage"
bound = true

[[acceptance]]
text = "given a bearer-token request with no cookie, when state-changing calls are made, then they behave exactly as before (game client unaffected)"
bound = false
+++

Follow-up to ~7PR4BF7 (INV-006). The web client now keeps the bearer token in memory only, so a page reload signs the user out. To restore sessions across reloads without script-readable storage, the API should issue the session as an HttpOnly, Secure, SameSite cookie from login in api/auth.py, accept it as an alternative to the Authorization header, and add CSRF protection plus a CORS credentials review (INV-004). Then the web client can call a session-restore endpoint on load. Not done in ~7PR4BF7 because api/auth.py is being edited on a sibling lognd branch.
