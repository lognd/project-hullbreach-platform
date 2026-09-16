---
id: T-0094
title: Replay ingestion endpoint and match replay page (design spike first)
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0093
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/replays.py
- web/src/pages/Replay.tsx
- tests/unit/test_replays.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a recorded input log, when uploaded, then the replay page renders both
    ships
  evidence: []
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
