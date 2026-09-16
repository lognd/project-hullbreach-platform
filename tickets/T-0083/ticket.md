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
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/admin/items.py
- src/hullbreach_server/services/catalog.py
- tests/unit/test_admin_items.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a retired item, when the public catalog is fetched, then it is absent;
    when an owner's inventory is fetched, then present
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
