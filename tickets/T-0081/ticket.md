---
id: T-0081
title: Admin void-match endpoint reversing rating and currency effects
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0079
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
- src/hullbreach_server/api/admin/matches.py
- src/hullbreach_server/services/matches.py
- tests/unit/test_admin_void.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a voided match, when both players' balances and ratings are read, then
    they equal the pre-match values
  evidence: []
threat: null
component: null
labels:
- jira:SCRUM-196
- owner:lognd
anchor: false
anchor_reason: null
land_commit: null
---
