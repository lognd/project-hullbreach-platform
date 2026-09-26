---
id: T-0076
title: Admin player search and detail endpoints under /api/v1/admin
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
- src/hullbreach_server/api/admin/players.py
- src/hullbreach_server/services/admin.py
- tests/unit/test_admin_players.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a partial username, when searched by an admin, then matching players
    return; a Player gets 403
  evidence: []
threat: null
component: null
labels:
- jira:SCRUM-192
- owner:lognd
anchor: false
anchor_reason: null
land_commit: null
---
