---
id: T-0064
title: E6 Store and item catalog
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: high
parent: null
tier: epic
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/catalog.py
- src/hullbreach_server/api/store.py
- src/hullbreach_server/db/migrations/
- src/hullbreach_server/db/models/inventory.py
- src/hullbreach_server/db/models/item.py
- src/hullbreach_server/db/models/ledger.py
- src/hullbreach_server/services/catalog.py
- src/hullbreach_server/services/currency.py
- src/hullbreach_server/services/matches.py
- src/hullbreach_server/services/store.py
- tests/unit/test_catalog.py
- tests/unit/test_currency.py
- tests/unit/test_item_models.py
- tests/unit/test_store_purchase.py
- web/src/components/ItemCard.tsx
- web/src/pages/Store.tsx
- web/tests/unit/Store.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
Epic from the Module 4 story map. Stories:
- S20 Browse the catalog
- S21 Earn currency by playing
- S22 Buy an item
