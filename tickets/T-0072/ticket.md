---
id: T-0072
title: POST /api/v1/store/purchase as a single transaction with a uniqueness constraint
  on (user, item)
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0071
tier: ticket
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/store.py
- src/hullbreach_server/services/store.py
- tests/unit/test_store_purchase.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given two concurrent purchases of one item, when both run, then one succeeds
    and one is refused with no double debit
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
