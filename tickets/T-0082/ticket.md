---
id: T-0082
title: S25 Curate the item catalog
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0074
tier: story
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/admin/items.py
- src/hullbreach_server/services/catalog.py
- tests/unit/test_admin_items.py
- web/src/pages/admin/Items.tsx
- web/tests/unit/AdminItems.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given an admin, when they create an item or change its name, price, category,
    or preview, or retire it, then it saves
  evidence: []
- text: given a retired item, when the store loads, then it is absent, but owners
    keep it
  evidence: []
- text: given a catalog change, when players reload, then they see it without a redeploy
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a administrator, I want to add, edit, price, and retire catalog items, so that the store can change without a code deploy.

Open questions:
- Preview images: uploaded through the admin UI, or referenced by URL?
- Retiring an item: hide from the store but keep it for owners?
