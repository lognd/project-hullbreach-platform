---
id: T-0034
title: PATCH /api/v1/me with current-password confirmation and session invalidation
  on password change
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0033
tier: ticket
sprint: sprint-2
runs_last: false
milestone: 0.2.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/me.py
- src/hullbreach_server/auth/sessions.py
- tests/unit/test_me_edit.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a password change, when it succeeds, then every other session for that
    user is revoked
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
