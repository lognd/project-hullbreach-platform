---
id: T-0020
title: POST /api/v1/auth/login issuing a token, with failed-login rate limiting
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
- src/hullbreach_server/api/auth.py
- tests/unit/test_auth_login.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
evidence:
- tests/unit/test_auth_login.py::test_sixth_failed_login_attempt_in_window_returns_429
designated_repro_test: null
acceptance:
- text: given five failed attempts in a minute, when a sixth arrives, then 429
  evidence:
  - tests/unit/test_auth_login.py::test_sixth_failed_login_attempt_in_window_returns_429
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
