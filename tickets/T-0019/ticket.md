---
id: T-0019
title: Session model with expiry and revocation, and the current-user auth dependency
state: done
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0018
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/db/models/session.py
- src/hullbreach_server/auth/sessions.py
- src/hullbreach_server/auth/deps.py
- tests/unit/test_sessions.py
- src/hullbreach_server/db/models/__init__.py
- src/hullbreach_server/db/migrations/versions/*.py
- .env.example
- docs/index.md
- design/hullbreach.strata
- docs/design/sprint-1.md
- docs/design/registry/capability-via-ratchet.lock.json
- tests/unit/test_roles.py
- src/hullbreach_server/auth/__init__.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: src/hullbreach_server/db/models/__init__.py
  reason: Session must be re-exported here so Base.metadata (and Alembic autogenerate)
    sees it, per env.py's own comment naming T-0019
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/db/migrations/versions/*.py
  reason: session migration file lives under versions/, needed to create the sessions
    table
  actor: logan
  at: '2026-09-16'
- op: add
  glob: .env.example
  reason: documents HULLBREACH_SESSION_TTL_SECONDS per docs/design/sprint-1.md section
    3, brief-allowed config exception
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: add frob:doc anchors for the new Session/sessions.py/deps.py public API,
    re-point the REL200 waivers off T-0019 to their real successors, add the SYS100
    env.read capability on hullbreach_server_auth and the auth->logging Flow
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: add frob:doc anchors for the new Session/sessions.py/deps.py public API,
    re-point the REL200 waivers off T-0019 to their real successors, add the SYS100
    env.read capability on hullbreach_server_auth and the auth->logging Flow
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/sprint-1.md
  reason: AFFECT001 on the new f_auth_to_logging flow needs its section-9 doc touched,
    and SELFAUDIT001/SYS111's env.read ratchet on hullbreach_server_auth needs raising
    to 1 with a reason
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/registry/capability-via-ratchet.lock.json
  reason: AFFECT001 on the new f_auth_to_logging flow needs its section-9 doc touched,
    and SELFAUDIT001/SYS111's env.read ratchet on hullbreach_server_auth needs raising
    to 1 with a reason
  actor: logan
  at: '2026-09-16'
- op: add
  glob: tests/unit/test_roles.py
  reason: T-0019 makes hullbreach_server.auth.sessions importable for the first time,
    which flips ruff's I001 classification of this pre-existing xfail test's import
    block from unresolvable to first-party-but-unsorted, turning a previously-latent
    lint bug into a real CI failure on main; fixing only the import order (no xfail/logic
    change, T-0028's own test content untouched)
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/auth/__init__.py
  reason: frob-exports flagged 9 public auth symbols missing from the package __init__;
    export them per the codebase's db/__init__.py convention
  actor: logan
  at: '2026-09-16'
evidence:
- tests/unit/test_sessions.py::test_expired_token_returns_401
- tests/unit/test_sessions.py::test_revoked_token_returns_401
designated_repro_test: null
acceptance:
- text: given an expired or revoked token, when a protected route is called, then
    401
  evidence:
  - tests/unit/test_sessions.py::test_expired_token_returns_401
  - tests/unit/test_sessions.py::test_revoked_token_returns_401
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
