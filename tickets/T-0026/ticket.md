---
id: T-0026
title: Bearer-token login for the game client and GET /api/v1/auth/session for server-side
  validation
state: queued
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
- src/hullbreach_server/api/auth.py
- src/hullbreach_server/auth/deps.py
- tests/unit/test_auth_game.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
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
