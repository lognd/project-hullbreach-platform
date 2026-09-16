---
id: T-0019
title: Session model with expiry and revocation, and the current-user auth dependency
state: queued
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
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
evidence:
- tests/unit/test_sessions.py::test_expired_token_returns_401
designated_repro_test: null
acceptance:
- text: given an expired or revoked token, when a protected route is called, then
    401
  evidence:
  - tests/unit/test_sessions.py::test_expired_token_returns_401
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
