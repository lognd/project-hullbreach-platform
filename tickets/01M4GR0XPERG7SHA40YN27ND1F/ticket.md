+++
id = "01M4GR0XPERG7SHA40YN27ND1F"
title = "register: concurrent duplicate signup surfaces unhandled IntegrityError as HTTP 500"
type = "bug"
category = "todo"
priority = "high"
reporter = "lognd"
created = "2026-10-09T16:30:29Z"
updated = "2026-10-09T16:30:29Z"
labels = ["origin:auditor", "audit:db"]
scope = ["src/hullbreach_server/api/auth.py"]
+++

api/auth.py:68-83 (register) + db/models/user.py:114,118. Contract: _duplicate_field is a check-then-insert (TOCTOU); the DB unique constraints uq_users_username/uq_users_email are the real guarantee, but db.commit() at api/auth.py:82 does not handle sqlalchemy.exc.IntegrityError, so two concurrent registrations (or a case-variant email, since the unique index is case-sensitive and RegisterRequest.email is not normalized) yield 500 instead of the documented 409 with field. Also no db.rollback on failure. Fix: wrap add/commit in try/except IntegrityError -> rollback and map the violated constraint name to the 409 {field}; normalize email (lowercase) before the pre-query and insert. Add a test that forces the race (insert the row between pre-query and commit) against a real session.
