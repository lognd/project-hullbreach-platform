---
id: T-0023
title: POST /api/v1/auth/logout revoking the current session (and optionally all sessions)
state: done
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0022
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/auth.py
- tests/unit/test_auth_logout.py
- src/hullbreach_server/auth/schemas.py
- tests/unit/test_auth_game.py
- docs/index.md
- design/hullbreach.strata
- src/hullbreach_server/auth/deps.py
- src/hullbreach_server/auth/sessions.py
- src/hullbreach_server/db/models/session.py
- src/hullbreach_server/db/migrations/versions/*.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: src/hullbreach_server/auth/schemas.py
  reason: tests/unit/test_auth_logout.py's own revocation checks (3 of its 5 tests)
    call GET /api/v1/auth/session as the only existing protected endpoint to prove
    a token is now rejected; that route does not exist yet (T-0026's ticket), so T-0023
    implements the minimal GET /session (SessionInfo schema + route via get_current_user)
    needed to make its own tests runnable, which trivially satisfies 3 of T-0026's
    own pre-written xfail tests in test_auth_game.py (player_id/role, missing token,
    malformed token) since get_current_user already handles all three cases uniformly;
    T-0026's remaining scope (the game-client login path) is untouched
  actor: logan
  at: '2026-09-16'
- op: add
  glob: tests/unit/test_auth_game.py
  reason: tests/unit/test_auth_logout.py's own revocation checks (3 of its 5 tests)
    call GET /api/v1/auth/session as the only existing protected endpoint to prove
    a token is now rejected; that route does not exist yet (T-0026's ticket), so T-0023
    implements the minimal GET /session (SessionInfo schema + route via get_current_user)
    needed to make its own tests runnable, which trivially satisfies 3 of T-0026's
    own pre-written xfail tests in test_auth_game.py (player_id/role, missing token,
    malformed token) since get_current_user already handles all three cases uniformly;
    T-0026's remaining scope (the game-client login path) is untouched
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: document POST /auth/logout and GET /auth/session in the Auth API section;
    re-point/remove REL200 and WIRE001 waivers this ticket resolves
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: document POST /auth/logout and GET /auth/session in the Auth API section;
    re-point/remove REL200 and WIRE001 waivers this ticket resolves
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/auth/deps.py
  reason: 'remove/re-point WIRE001 waivers that named T-0023 as follow_up: get_current_user,
    revoke_session, and revoke_all_sessions are all called by logout/session now (waivers
    resolved, removed); the migration files'' permanent Alembic-reflection waivers
    and the Session TypeDecorator waiver still need a live tracker, re-pointed to
    T-0026'
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/auth/sessions.py
  reason: 'remove/re-point WIRE001 waivers that named T-0023 as follow_up: get_current_user,
    revoke_session, and revoke_all_sessions are all called by logout/session now (waivers
    resolved, removed); the migration files'' permanent Alembic-reflection waivers
    and the Session TypeDecorator waiver still need a live tracker, re-pointed to
    T-0026'
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/db/models/session.py
  reason: 'remove/re-point WIRE001 waivers that named T-0023 as follow_up: get_current_user,
    revoke_session, and revoke_all_sessions are all called by logout/session now (waivers
    resolved, removed); the migration files'' permanent Alembic-reflection waivers
    and the Session TypeDecorator waiver still need a live tracker, re-pointed to
    T-0026'
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/db/migrations/versions/*.py
  reason: 'remove/re-point WIRE001 waivers that named T-0023 as follow_up: get_current_user,
    revoke_session, and revoke_all_sessions are all called by logout/session now (waivers
    resolved, removed); the migration files'' permanent Alembic-reflection waivers
    and the Session TypeDecorator waiver still need a live tracker, re-pointed to
    T-0026'
  actor: logan
  at: '2026-09-16'
evidence:
- tests/unit/test_auth_logout.py::test_logout_revokes_token_so_it_is_rejected_afterward
designated_repro_test: null
acceptance:
- text: given a valid session, when logout is called, then that token is rejected
    afterwards
  evidence:
  - tests/unit/test_auth_logout.py::test_logout_revokes_token_so_it_is_rejected_afterward
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
