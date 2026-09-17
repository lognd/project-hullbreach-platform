---
id: T-0026
title: Bearer-token login for the game client and GET /api/v1/auth/session for server-side
  validation
state: done
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0025
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- tests/unit/test_auth_game.py
- docs/index.md
- design/hullbreach.strata
- src/hullbreach_server/db/migrations/versions/*.py
- src/hullbreach_server/db/models/session.py
- web/src/api/auth.ts
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: remove
  glob: src/hullbreach_server/api/auth.py
  reason: GET /api/v1/auth/session was already implemented and fully tested by T-0023
    (merged), and the design's f_login_game flow reuses the existing POST /auth/login
    endpoint verbatim (attr 'POST /api/v1/auth/login', same as f_login_web) rather
    than a separate route -- no code change is needed in either file for T-0026's
    acceptance criterion
  actor: logan
  at: '2026-09-16'
- op: remove
  glob: src/hullbreach_server/auth/deps.py
  reason: GET /api/v1/auth/session was already implemented and fully tested by T-0023
    (merged), and the design's f_login_game flow reuses the existing POST /auth/login
    endpoint verbatim (attr 'POST /api/v1/auth/login', same as f_login_web) rather
    than a separate route -- no code change is needed in either file for T-0026's
    acceptance criterion
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: note the game client reuses POST /auth/login verbatim in the Auth API section;
    re-point/resolve the f_login_game and f_session_token_to_game_client REL200 waivers
    now that both the login and session endpoints are real
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: note the game client reuses POST /auth/login verbatim in the Auth API section;
    re-point/resolve the f_login_game and f_session_token_to_game_client REL200 waivers
    now that both the login and session endpoints are real
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/db/migrations/versions/*.py
  reason: re-point the permanent Alembic-reflection/TypeDecorator WIRE001 waivers
    that named T-0026 as follow_up (no ticket can ever statically wire them) to T-0028,
    the next open ticket touching this area
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/db/models/session.py
  reason: re-point the permanent Alembic-reflection/TypeDecorator WIRE001 waivers
    that named T-0026 as follow_up (no ticket can ever statically wire them) to T-0028,
    the next open ticket touching this area
  actor: logan
  at: '2026-09-16'
- op: add
  glob: web/src/api/auth.ts
  reason: T-0026 closing strands fetchSession's WIRE001 waiver (follow_up named T-0026);
    GET /session is designed for the game server to call directly, never this web
    client, so the waiver is genuinely permanent -- mark it permanent=true rather
    than re-pointing to another ticket that will never wire it either
  actor: logan
  at: '2026-09-16'
evidence:
- tests/unit/test_auth_game.py::test_session_endpoint_returns_player_id_and_role_for_valid_token
- tests/unit/test_auth_game.py::test_session_endpoint_returns_401_for_missing_token
- tests/unit/test_auth_game.py::test_session_endpoint_returns_401_for_malformed_token
- tests/unit/test_auth_game.py::test_session_endpoint_omits_username_and_email
designated_repro_test: null
acceptance:
- text: given a client token, when the game server calls the session endpoint, then
    it gets the player id and role
  evidence:
  - tests/unit/test_auth_game.py::test_session_endpoint_returns_player_id_and_role_for_valid_token
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
