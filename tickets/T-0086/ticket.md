---
id: T-0086
title: 'S29 Find an online opponent (platform half: matchmaking queue API)'
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
- src/hullbreach_server/api/matchmaking.py
- src/hullbreach_server/services/matchmaking.py
- tests/unit/test_matchmaking.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a signed-in player, when they enter the queue, then they can see they
    are queued and cancel
  evidence: []
- text: given two queued players within the rating window, when matched, then both
    receive the same game server address without typing one
  evidence: []
- text: given a matched game, when it ends, then it is recorded as ranked
  evidence: []
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want to queue for a ranked match and be paired with an opponent of similar rating, so that matches are fair and I do not have to arrange them myself.

Open questions:
- Who runs matchmaking: the platform API, or a lobby service on the game server host?
- Widening rating window over time in queue? Maximum wait before matching anyone?
- How many game servers do we run, and where?
