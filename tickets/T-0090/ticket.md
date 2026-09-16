---
id: T-0090
title: 'S49 Favor the defender and forgive honest lag (platform half: trust events)'
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0085
tier: story
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/admin/players.py
- src/hullbreach_server/api/trust.py
- src/hullbreach_server/db/models/trust.py
- tests/unit/test_trust_events.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given an authenticated game server, when it posts a trust event, then it is
    stored against the player and match
  evidence: []
- text: given an admin, when they view a player, then trust events are listed
  evidence: []
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
As a administrator, I want trust events from the game server logged and visible on the platform, so that repeated implausible claims are reviewable rather than lost in server logs.

Open questions:
- Are trust events reported to the platform for admins to see?
- What does the server do at minimum trust: reject claims, or end the match?
