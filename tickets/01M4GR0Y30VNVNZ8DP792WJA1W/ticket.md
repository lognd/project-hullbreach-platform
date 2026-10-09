+++
id = "01M4GR0Y30VNVNZ8DP792WJA1W"
title = "seed(): DB failures and bad inputs escape the Result contract (IntegrityError, KeyError)"
type = "bug"
category = "done"
outcome = "fixed"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:29Z"
updated = "2026-10-09T17:11:07Z"
labels = ["origin:auditor", "audit:db"]
scope = ["src/hullbreach_server/db/seed.py"]

[[acceptance]]
text = "given a conflicting admin, bad credentials, bad seed data or a database error, when seed runs, then it returns Err and rolls back"
bound = true
+++

db/seed.py:127-139 (seed), :95-112 (_upsert_items), :115-140 (_create_first_admin). Contract: seed returns Result[None, SeedError] but SeedError has only MissingAdminPassword (seed.py:51). Unhandled: IntegrityError when HULLBREACH_ADMIN_USERNAME/EMAIL collides with an existing non-admin user (default username 'admin' / admin@example.com), SQLAlchemyError on connect/commit, KeyError/JSONDecodeError from seed_items.json (item['price'], seed.py:106), and no length/format validation of env username/email against the String(32)/String(254) columns. These propagate as tracebacks through __main__._db_seed (__main__.py:37-45) instead of the clean 'db seed failed' exit 1. Fix: add SeedError variants (AdminConflict, DatabaseFailure, InvalidSeedData, InvalidAdminCredentials), catch SQLAlchemyError/ValueError at the boundary with rollback, validate env inputs.
