---
id: T-0023
title: POST /api/v1/auth/logout revoking the current session (and optionally all sessions)
state: queued
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
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a valid session, when logout is called, then that token is rejected
    afterwards
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
