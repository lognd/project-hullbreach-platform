---
id: T-0021
title: Website login page and persisted session across reloads
state: in-progress
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
- web/src/router.tsx
- docs/index.md
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: web/src/router.tsx
  reason: wire the new Login page into the /login route now that it exists, replacing
    T-0044's inline placeholder
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: documenting web/src/pages/Login.tsx (new caller of login()) and the doc-as-you-go
    convention for frob:doc anchors
  actor: logan
  at: '2026-09-16'
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
