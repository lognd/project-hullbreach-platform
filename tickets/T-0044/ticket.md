---
id: T-0044
title: Router, page shell, header and footer components with signed-in and signed-out
  states
state: in-progress
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0043
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- web/src/App.tsx
- web/src/components/Header.tsx
- web/src/components/Footer.tsx
- web/src/router.tsx
- web/tests/unit/Header.test.tsx
- web/src/auth/session.ts
- web/src/main.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: web/src/auth/session.ts
  reason: router.tsx needs createBrowserRouter wired into main.tsx to replace the
    bare App render, and Header's signed-in state requires the useSession/saveSession/clearSession
    shape design/sprint-1.md sec.6 puts in auth/session.ts; T-0021 (already scoped
    to this same file) fills in Login.tsx's usage and reload-persistence coverage
    on top of this shape
  actor: logan
  at: '2026-09-16'
- op: add
  glob: web/src/main.tsx
  reason: router.tsx needs createBrowserRouter wired into main.tsx to replace the
    bare App render, and Header's signed-in state requires the useSession/saveSession/clearSession
    shape design/sprint-1.md sec.6 puts in auth/session.ts; T-0021 (already scoped
    to this same file) fills in Login.tsx's usage and reload-persistence coverage
    on top of this shape
  actor: logan
  at: '2026-09-16'
designated_repro_test: null
acceptance:
- text: given the header, when tabbing through, then focus order matches visual order
    and every control activates with Enter
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
