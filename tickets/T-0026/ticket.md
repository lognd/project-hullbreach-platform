---
id: T-0026
title: Bearer-token login for the game client and GET /api/v1/auth/session for server-side
  validation
state: in-progress
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
evidence:
- tests/unit/test_auth_game.py::test_session_endpoint_returns_player_id_and_role_for_valid_token
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
