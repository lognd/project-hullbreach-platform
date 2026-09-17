---
id: T-0017
title: Website register page with inline validation errors
state: done
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
- web/src/router.tsx
- docs/index.md
- design/hullbreach.strata
- docs/design/registry/capability-via-ratchet.lock.json
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: web/src/router.tsx
  reason: wire the new Register page into the / -> /register route now that it exists,
    replacing T-0044's inline placeholder
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: documenting web/src/api/auth.ts and web/src/pages/Register.tsx in the same
    change, per the doc-as-you-go convention
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: web/src/api/auth.ts uses window.fetch (register/login/logout/fetchSession);
    the browser node's capability declaration must grant fetch_url via that real file,
    or SELFAUDIT001 flags an undeclared observed capability
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/registry/capability-via-ratchet.lock.json
  reason: 'SYS111 ratchet: browser node''s fetch_url via-list grew from 0 to 1 site
    (web/src/api/auth.ts) with T-0017''s may declaration; raising accepted_count in
    the same diff per the ratchet''s own requirement'
  actor: logan
  at: '2026-09-16'
evidence:
- web/tests/unit/Register.test.tsx::Register page > shows field error next to the
  offending input
designated_repro_test: null
acceptance:
- text: given the register form, when the API returns a field error, then it is shown
    next to the field
  evidence:
  - web/tests/unit/Register.test.tsx::Register page > shows field error next to the
    offending input
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
