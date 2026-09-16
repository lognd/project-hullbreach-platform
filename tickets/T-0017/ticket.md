---
id: T-0017
title: Website register page with inline validation errors
state: in-progress
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0014
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- web/src/pages/Register.tsx
- web/src/api/auth.ts
- web/tests/unit/Register.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given the register form, when the API returns a field error, then it is shown
    next to the field
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
