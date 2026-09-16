---
id: T-0079
title: S24 Correct a player's rating
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0074
tier: story
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/admin/matches.py
- src/hullbreach_server/api/admin/ratings.py
- src/hullbreach_server/services/admin.py
- src/hullbreach_server/services/matches.py
- tests/unit/test_admin_ratings.py
- tests/unit/test_admin_void.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a rating value and reason, when an admin sets it, then the change appears
    in the player's rating history with the reason
  evidence: []
- text: given a recorded match, when an admin voids it, then its rating and currency
    effects are reversed for both players
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a administrator, I want to reset or adjust a player's rating, so that I can undo the effect of a cheated or bugged match.

Open questions:
- Adjust to a specific value, or only reset to the starting rating?
- Should voiding a match automatically re-run the rating change for both players?
