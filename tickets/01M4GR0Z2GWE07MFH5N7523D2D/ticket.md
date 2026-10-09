+++
id = "01M4GR0Z2GWE07MFH5N7523D2D"
title = "User.role CHECK constraint promised by migration/docs is not created; no Postgres integration coverage for db boundary"
type = "bug"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:30Z"
updated = "2026-10-09T17:11:59Z"
labels = ["origin:auditor", "audit:db"]
scope = ["src/hullbreach_server/db/models/user.py", "src/hullbreach_server/db/migrations/versions/0f6d70e4d209_create_users_table.py"]

[[acceptance]]
text = "given a migrated database, when an unknown role is inserted, then the database rejects it"
bound = true
+++

db/models/user.py:123-132 and migrations/versions/0f6d70e4d209_create_users_table.py:3-8,29-33. The migration docstring says role is 'VARCHAR with a CHECK constraint', but sa.Enum(native_enum=False) defaults create_constraint=False in SQLAlchemy 2.x, so no CHECK exists and the database accepts any role string (e.g. a raw-SQL 'superadmin'); the compare_metadata test cannot catch it because model and migration agree. Also all db tests (tests/unit/test_db_engine.py, test_seed.py, tests/system/test_build.py:107) run on SQLite or only with an unreachable host; nothing exercises Postgres (the production dialect: seed.py postgresql insert branch, timestamptz, FK cascade, server_default). Fix: set create_constraint=True in model and a new migration adding ck_users_role (or correct the doc), and add a Postgres-backed integration test (testcontainers/CI service) running upgrade head, seed twice, register/login/session round trip.
