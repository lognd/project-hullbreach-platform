+++
id = "01M4GR0D9K7NFS09E62D5KPH93"
title = "get_current_user is async but runs blocking SQLAlchemy calls on the event loop for every authenticated api route"
type = "bug"
category = "done"
outcome = "duplicate"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:12Z"
updated = "2026-10-09T16:36:04Z"
labels = ["origin:auditor", "interface-audit"]
scope = ["src/hullbreach_server/auth/deps.py"]
+++

Consumed by api/auth.py:160,177 (logout, session) and every queued route (T-0031.. mount behind it). auth/deps.py:41 'async def get_current_user' calls resolve_session (sessions.py:240, db.query(...).first()) and db.get (:56) synchronously, blocking the event loop during DB I/O, while the sync route handlers and get_db run in the threadpool. Under load the auth dependency serializes all requests, including /health. Also get_db's session is shared with the sync route via the dependency cache across threads. Fix: make get_current_user and require_admin plain 'def' so FastAPI runs them in the threadpool (no behavior change), and add a test asserting they are not coroutine functions.
