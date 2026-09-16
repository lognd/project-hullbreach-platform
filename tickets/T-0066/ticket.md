---
id: T-0066
title: Item and Inventory models with categories and migration
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0065
tier: ticket
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/db/models/item.py
- src/hullbreach_server/db/models/inventory.py
- src/hullbreach_server/db/migrations/
- tests/unit/test_item_models.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given the seed, when items are loaded, then every item has a category from
    the enum
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
