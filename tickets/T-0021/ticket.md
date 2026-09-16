---
id: T-0021
title: Website login page and persisted session across reloads
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0018
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- web/src/pages/Login.tsx
- web/src/auth/session.ts
- web/tests/unit/Login.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a login, when the page reloads, then the user is still shown as signed
    in
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
