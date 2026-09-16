---
id: T-0093
title: S52 Watch a match from the website
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0092
tier: story
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/replays.py
- tests/unit/test_replays.py
- web/src/pages/Replay.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a match page, when opened, then the match plays back with both ships
    and the arena
  evidence: []
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
As a visitor, I want to spectate a live or recorded match in the browser, so that I can see the game before installing it.

Open questions:
- Live relay from the game server, or replay from recorded inputs?
