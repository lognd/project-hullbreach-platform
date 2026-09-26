---
id: T-0077
title: Suspension state with ModerationLog rows; login refuses suspended players with
  the reason
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0075
tier: ticket
sprint: sprint-3
runs_last: false
milestone: 0.3.0
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
- src/hullbreach_server/db/models/moderation.py
- src/hullbreach_server/api/admin/players.py
- src/hullbreach_server/api/auth.py
- tests/unit/test_moderation.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a suspended player, when they log in, then 403 carrying the suspension
    reason
  evidence: []
threat: null
component: null
labels:
- jira:SCRUM-193
- owner:lognd
anchor: false
anchor_reason: null
land_commit: null
---
