---
id: T-0083
title: Admin item CRUD endpoints with retire semantics
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0082
tier: ticket
sprint: sprint-3
runs_last: false
milestone: 0.3.0
flavour: null
due: null
rank: null
points: 3
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
- src/hullbreach_server/api/admin/items.py
- src/hullbreach_server/services/catalog.py
- tests/unit/test_admin_items.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
triage_changes:
- field: points
  old_value: null
  new_value: '3'
  reason: ticket sizing
  actor: logan
  at: '2026-09-26'
designated_repro_test: null
acceptance:
- text: given a retired item, when the public catalog is fetched, then it is absent;
    when an owner's inventory is fetched, then present
  evidence: []
threat: null
component: null
labels:
- jira:SCRUM-197
- owner:lognd
anchor: false
anchor_reason: null
land_commit: null
---
