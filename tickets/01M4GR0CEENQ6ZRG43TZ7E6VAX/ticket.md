+++
id = "01M4GR0CEENQ6ZRG43TZ7E6VAX"
title = "register: unique-race IntegrityError and over-long username surface as 500 instead of 409/422"
type = "bug"
category = "todo"
priority = "high"
reporter = "lognd"
created = "2026-10-09T16:30:11Z"
updated = "2026-10-09T17:02:06Z"
labels = ["origin:auditor", "interface-audit"]
scope = ["src/hullbreach_server/api/auth.py", "src/hullbreach_server/auth/schemas.py"]

[[acceptance]]
text = "given a lost insert race, an over-long username or a case-variant duplicate, when registering, then the API answers 409 or 422, never 500"
bound = true
+++

api/auth.py:91-105 register(). Contract: 201, or 409 naming the field, or 422 on bad input; docstring promises no other failure. Gaps: (1) _duplicate_field pre-query then db.commit() at :105 is a TOCTOU; two concurrent registers for one username/email hit the unique constraint, IntegrityError is uncaught -> 500 and session left dirty. (2) auth/schemas.py:310 RegisterRequest.username has no max_length/min_length/strip but users.username is String(32) (db/models/user.py) so a 33+ char username raises DataError on Postgres -> 500 (SQLite does not enforce, masking it in unit tests); empty/whitespace usernames accepted. (3) username/email uniqueness is case-sensitive: 'Bob@x.com' and 'bob@x.com' both register. Fix: catch sqlalchemy.exc.IntegrityError around commit, db.rollback(), map to the same 409 body (determine field by re-running _duplicate_field); add Field(min_length=3,max_length=32) + pattern to username; normalize email to lower-case on input and compare case-insensitively (or unique index on lower()). Add a Postgres-backed integration test for the 33-char and race cases.
