---
id: T-0091
title: POST /api/v1/trust-events from the game server and listing on the admin player
  detail
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0090
tier: ticket
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/trust.py
- src/hullbreach_server/db/models/trust.py
- src/hullbreach_server/api/admin/players.py
- tests/unit/test_trust_events.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a posted trust event, when the admin detail is fetched, then it appears
    with time and kind
  evidence: []
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
