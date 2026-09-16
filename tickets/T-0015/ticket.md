---
id: T-0015
title: User model, migration, and password hashing helper
state: in-progress
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0014
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/db/models/user.py
- src/hullbreach_server/auth/passwords.py
- tests/unit/test_passwords.py
- src/hullbreach_server/auth/__init__.py
- src/hullbreach_server/db/models/__init__.py
- src/hullbreach_server/db/migrations/versions/
- src/hullbreach_server/db/migrations/env.py
- pyproject.toml
- uv.lock
- tests/unit/test_roles.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: src/hullbreach_server/auth/__init__.py
  reason: new auth/ and db/models/ packages need __init__.py; the users migration
    (T-0015's acceptance criterion 'alembic heads match the models' via T-0007's env.py)
    lands under db/migrations/versions/, per the coordinator's explicit instruction
    to add the real users migration there
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/db/models/__init__.py
  reason: new auth/ and db/models/ packages need __init__.py; the users migration
    (T-0015's acceptance criterion 'alembic heads match the models' via T-0007's env.py)
    lands under db/migrations/versions/, per the coordinator's explicit instruction
    to add the real users migration there
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/db/migrations/versions/
  reason: new auth/ and db/models/ packages need __init__.py; the users migration
    (T-0015's acceptance criterion 'alembic heads match the models' via T-0007's env.py)
    lands under db/migrations/versions/, per the coordinator's explicit instruction
    to add the real users migration there
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/db/migrations/env.py
  reason: env.py must import db.models so Base.metadata is populated before compare_metadata/autogenerate
    runs, per docs/design/sprint-1.md section 1's own module map ('db/migrations/env.py
    imports Base and every model module from db/models/')
  actor: logan
  at: '2026-09-16'
- op: add
  glob: pyproject.toml
  reason: pyproject.toml/uv.lock gain the pwdlib[argon2] dependency
  actor: logan
  at: '2026-09-16'
- op: add
  glob: uv.lock
  reason: pyproject.toml/uv.lock gain the pwdlib[argon2] dependency
  actor: logan
  at: '2026-09-16'
- op: add
  glob: tests/unit/test_roles.py
  reason: landing db/models/user.py (Role, User) makes two of T-0028's xfail tests
    (enum membership, default role) genuinely pass -- same class of fixture-activation
    ripple as T-0006's; fixing inline rather than leaving a false XPASS(strict) failure
    in CI
  actor: logan
  at: '2026-09-16'
evidence:
- tests/unit/test_passwords.py::test_hash_password_verifies_and_does_not_store_plaintext
designated_repro_test: null
acceptance:
- text: given a password, when hashed, then verify succeeds and the stored value is
    not the password
  evidence:
  - tests/unit/test_passwords.py::test_hash_password_verifies_and_does_not_store_plaintext
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
