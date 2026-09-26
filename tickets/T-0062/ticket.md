---
id: T-0062
title: GET /api/v1/leaderboard with the caller's own rank
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0061
tier: ticket
sprint: sprint-3
runs_last: false
milestone: 0.3.0
flavour: null
due: null
rank: null
points: 2
unsized_ack: false
unsized_ack_reason: null
tokens_in: null
tokens_out: null
tokens_cache_read: null
usage: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
worktree: null
branch: null
scope:
- src/hullbreach_server/api/leaderboard.py
- src/hullbreach_server/services/leaderboard.py
- tests/unit/test_leaderboard.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
triage_changes:
- field: points
  old_value: null
  new_value: '2'
  reason: ticket sizing
  actor: logan
  at: '2026-09-26'
designated_repro_test: null
acceptance:
- text: given a player ranked 340, when they fetch the top 100, then the response
    includes their rank 340
  evidence: []
threat: null
component: null
labels:
- jira:SCRUM-190
- owner:lognd
anchor: false
anchor_reason: null
land_commit: null
---
