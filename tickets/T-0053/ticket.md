---
id: T-0053
title: Match and MatchPlayerStats models with migration
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
- src/hullbreach_server/db/models/match.py
- src/hullbreach_server/db/migrations/
- tests/unit/test_match_models.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a match with two players, when saved, then both stat rows reference
    it
  evidence: []
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
