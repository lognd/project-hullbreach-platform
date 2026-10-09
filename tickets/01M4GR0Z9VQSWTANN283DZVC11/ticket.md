+++
id = "01M4GR0Z9VQSWTANN283DZVC11"
title = "__main__ _db_upgrade: cwd-relative alembic.ini and swallowed result; Session/User created_at tz handling inconsistent"
type = "bug"
category = "todo"
priority = "low"
reporter = "lognd"
created = "2026-10-09T16:30:31Z"
updated = "2026-10-09T17:11:15Z"
labels = ["origin:auditor", "audit:db"]
scope = ["src/hullbreach_server/__main__.py"]

[[acceptance]]
text = "given a cwd without alembic.ini, when db upgrade runs, then migrations apply, and failures exit 1 with a message"
bound = true
+++

__main__.py:24-29. alembic_main(['-c','alembic.ini',...]) resolves alembic.ini against the process cwd, so 'hullbreach_server db upgrade' run from any other directory (installed package, container workdir) fails with a CommandError traceback rather than a clear error; alembic.ini also is not a packaged file (script_location uses %(here)s). Fix: resolve the ini/script_location from the package (or pass a programmatic alembic Config with script_location from Path(__file__)), and print a clear stderr message + exit code on failure. Related minor gap: db/models/user.py:133-135 User.created_at uses plain DateTime(timezone=True) whereas Session columns use _UTCDateTime (models/session.py:34), so UserProfile.created_at (auth/schemas.py:68) is naive on SQLite and aware on Postgres; reuse one shared tz-aware type.
