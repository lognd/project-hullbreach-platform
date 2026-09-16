---
id: T-0016
title: POST /api/v1/auth/register with username, email, and password validation
state: queued
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
- src/hullbreach_server/api/auth.py
- src/hullbreach_server/auth/schemas.py
- tests/unit/test_auth_register.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
evidence:
- tests/unit/test_auth_register.py::test_register_duplicate_username_returns_409_with_field
- tests/unit/test_auth_register.py::test_register_valid_request_returns_201_with_player_defaults
designated_repro_test: null
acceptance:
- text: given a duplicate username, when registering, then 409 with a field-specific
    message
  evidence:
  - tests/unit/test_auth_register.py::test_register_duplicate_username_returns_409_with_field
- text: given a valid request, when registering, then 201 and role Player, currency
    0, rating default
  evidence:
  - tests/unit/test_auth_register.py::test_register_valid_request_returns_201_with_player_defaults
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
