---
id: T-0061
title: S19 See where I stand
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0050
tier: story
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/leaderboard.py
- src/hullbreach_server/services/leaderboard.py
- tests/unit/test_leaderboard.py
- web/src/pages/Leaderboard.tsx
- web/tests/unit/Leaderboard.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given any visitor, when the leaderboard loads, then rank, name, rating, and
    matches played show for the top players
  evidence: []
- text: given a logged-in player outside the visible range, when the leaderboard loads,
    then their own rank shows
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want a leaderboard of the top-rated players, so that I have someone to aim for.

Open questions:
- Top 100 only, or paginated? Show players with fewer than N matches?
