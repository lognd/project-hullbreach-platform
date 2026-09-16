---
id: T-0088
title: 'S35 Save and load ship designs (platform half: design storage)'
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0085
tier: story
sprint: sprint-2
runs_last: false
milestone: 0.2.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/designs.py
- src/hullbreach_server/db/models/design.py
- tests/unit/test_designs.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a named design, when saved and later loaded, then it round-trips unchanged
  evidence: []
- text: given a design that violates current rules, when loaded, then it is reported
    rather than silently altered
  evidence: []
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want to save a ship design and load it before a match, so that I do not rebuild from scratch every game.

Open questions:
- Local files, or stored on the platform under the account?
- Is a design validated on load against the current block rules?
