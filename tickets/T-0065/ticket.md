---
id: T-0065
title: S20 Browse the catalog
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
- src/hullbreach_server/api/catalog.py
- src/hullbreach_server/db/migrations/
- src/hullbreach_server/db/models/inventory.py
- src/hullbreach_server/db/models/item.py
- src/hullbreach_server/services/catalog.py
- tests/unit/test_catalog.py
- tests/unit/test_item_models.py
- web/src/components/ItemCard.tsx
- web/src/pages/Store.tsx
- web/tests/unit/Store.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given at least 100 items, when browsing by category, then name, preview, price,
    and owned flag show
  evidence: []
- text: given the website, when the catalog is served, then it comes from the database,
    not hard-coded
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want to browse skins and other items with names, previews, and prices, so that I can decide what to spend my currency on.

Open questions:
- Categories: skins, block cosmetics, trails, banners? Which ship in v1?
- Previews: static images, or rendered from the same assets the game uses?
