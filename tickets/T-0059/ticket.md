---
id: T-0059
title: GET /api/v1/me/matches with cursor pagination
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0058
tier: ticket
sprint: sprint-2
runs_last: false
milestone: 0.2.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/me.py
- src/hullbreach_server/services/matches.py
- tests/unit/test_me_matches.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given 250 matches, when paging with the cursor, then every match appears exactly
    once, newest first
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
