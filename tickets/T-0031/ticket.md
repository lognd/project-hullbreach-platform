---
id: T-0031
title: GET /api/v1/me aggregating profile, balance, inventory, and last five matches
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0030
tier: ticket
sprint: sprint-2
runs_last: false
milestone: 0.2.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/me.py
- src/hullbreach_server/services/profile.py
- tests/unit/test_me.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a player with matches and items, when GET /me is called, then all five
    sections are present
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
