---
id: T-0071
title: S22 Buy an item
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0064
tier: story
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/store.py
- src/hullbreach_server/services/store.py
- tests/unit/test_store_purchase.py
- web/src/components/ItemCard.tsx
- web/src/pages/Store.tsx
- web/tests/unit/Store.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given enough currency, when buying an unowned item, then the balance decreases
    and the item is in the inventory immediately
  evidence: []
- text: given insufficient currency or an owned item, when buying, then refused with
    a clear reason and no balance change
  evidence: []
- text: given two rapid purchase requests for the same item, when processed, then
    exactly one purchase results
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want to purchase an item with my currency, so that it appears in my inventory and can be equipped.

Open questions:
- Real-money payments are out of scope; confirm the store is currency-only.
- Refunds?
