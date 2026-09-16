---
id: T-0054
title: POST /api/v1/matches with an idempotency key, recording result and stats
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0051
tier: ticket
sprint: sprint-2
runs_last: false
milestone: 0.2.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/matches.py
- src/hullbreach_server/services/matches.py
- tests/unit/test_matches_record.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given the same idempotency key twice, when posted, then one match exists and
    both responses agree
  evidence: []
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
