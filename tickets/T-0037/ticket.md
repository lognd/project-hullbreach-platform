---
id: T-0037
title: DELETE /api/v1/me anonymizing the user and revoking sessions while keeping
  match rows
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0036
tier: ticket
sprint: sprint-2
runs_last: false
milestone: 0.2.0
flavour: null
due: null
rank: null
points: null
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
- src/hullbreach_server/api/me.py
- src/hullbreach_server/services/account_deletion.py
- tests/unit/test_me_delete.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a deleted user, when an opponent's match list is fetched, then the opponent
    name is a placeholder
  evidence: []
threat: null
component: null
labels:
- jira:SCRUM-149
- owner:lognd
anchor: false
anchor_reason: null
land_commit: null
---
