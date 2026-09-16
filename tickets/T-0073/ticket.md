---
id: T-0073
title: Website buy button with confirmation and error states
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
- web/src/components/ItemCard.tsx
- web/src/pages/Store.tsx
- web/tests/unit/Store.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given insufficient currency, when buy is pressed, then the refusal reason
    shows and the balance is unchanged
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
