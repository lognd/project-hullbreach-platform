+++
id = "01M4GS9A33TBP96SJ646TZCHZ0"
title = "Issue session as HttpOnly cookie so web can restore sessions after reload"
type = "security"
category = "todo"
priority = "low"
reporter = "a-carten"
created = "2026-10-09T16:52:32Z"
updated = "2026-10-09T16:52:32Z"
labels = ["owner:lognd"]
scope = ["src/hullbreach_server/api/auth.py"]
+++

Follow-up to ~7PR4BF7 (INV-006). The web client now keeps the bearer token in memory only, so a page reload signs the user out. To restore sessions across reloads without script-readable storage, the API should issue the session as an HttpOnly, Secure, SameSite cookie from login in api/auth.py, accept it as an alternative to the Authorization header, and add CSRF protection plus a CORS credentials review (INV-004). Then the web client can call a session-restore endpoint on load. Not done in ~7PR4BF7 because api/auth.py is being edited on a sibling lognd branch.
