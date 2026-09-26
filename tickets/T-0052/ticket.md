---
id: T-0052
title: Game-server API key authentication dependency
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
- src/hullbreach_server/auth/server_keys.py
- src/hullbreach_server/app/config.py
- tests/unit/test_server_keys.py
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
- text: given a missing or wrong key, when the match endpoint is called, then 401
  evidence: []
threat: null
component: null
labels:
- needs-game
- jira:SCRUM-136
- owner:lognd
anchor: false
anchor_reason: null
land_commit: null
---
