---
id: T-0067
title: GET /api/v1/catalog with category filter and owned flag for the caller
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
- src/hullbreach_server/api/catalog.py
- src/hullbreach_server/services/catalog.py
- tests/unit/test_catalog.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given an owned item, when the catalog is fetched signed in, then owned is
    true for it only
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
