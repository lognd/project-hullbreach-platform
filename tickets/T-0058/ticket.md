---
id: T-0058
title: S18 Browse my match history
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0050
tier: story
sprint: sprint-2
runs_last: false
milestone: 0.2.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/me.py
- src/hullbreach_server/services/matches.py
- tests/unit/test_me_matches.py
- web/src/pages/History.tsx
- web/tests/unit/History.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a player, when history is fetched, then matches are newest first with
    opponent, win/loss, date, duration, rating before and after, and stats
  evidence: []
- text: given hundreds of matches, when the list renders, then it stays responsive
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want a list of my past matches with opponent, result, rating change, and stats, so that I can see what worked and what did not.

Open questions:
- Pagination or infinite scroll? How many per page?
- Can a player open an opponent's history from a match row?
