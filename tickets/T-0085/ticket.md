---
id: T-0085
title: E13 Game server integration (platform half)
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: high
parent: null
tier: epic
sprint: sprint-2
runs_last: false
milestone: 0.2.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/admin/players.py
- src/hullbreach_server/api/designs.py
- src/hullbreach_server/api/matchmaking.py
- src/hullbreach_server/api/trust.py
- src/hullbreach_server/db/models/design.py
- src/hullbreach_server/db/models/trust.py
- src/hullbreach_server/services/matchmaking.py
- tests/unit/test_designs.py
- tests/unit/test_matchmaking.py
- tests/unit/test_trust_events.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
Epic from the Module 4 story map. Stories:
- S29 Find an online opponent (platform half: matchmaking queue API)
- S35 Save and load ship designs (platform half: design storage)
- S49 Favor the defender and forgive honest lag (platform half: trust events)
