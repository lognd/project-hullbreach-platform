---
id: T-0087
title: 'Queue endpoints: join, status, cancel, with rating-window pairing and server
  assignment'
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0086
tier: ticket
sprint: sprint-2
runs_last: false
milestone: 0.2.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/matchmaking.py
- src/hullbreach_server/services/matchmaking.py
- tests/unit/test_matchmaking.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given two players within 100 rating, when both are queued, then status returns
    the same match id and server address for both
  evidence: []
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
