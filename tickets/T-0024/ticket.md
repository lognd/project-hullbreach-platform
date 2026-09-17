---
id: T-0024
title: Logout control in the site header
state: in-progress
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0022
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- web/src/components/Header.tsx
- web/tests/unit/Header.test.tsx
- web/src/api/auth.ts
- web/src/auth/session.ts
- docs/index.md
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: web/src/api/auth.ts
  reason: removing the WIRE001 waiver on logout() now that Header.tsx calls it, and
    adding a frob:tests citation to Header.test.tsx
  actor: logan
  at: '2026-09-16'
- op: add
  glob: web/src/auth/session.ts
  reason: removing the WIRE001 waiver on clearSession() now that Header.tsx calls
    it on logout, and adding a frob:tests citation to Header.test.tsx
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: documenting the real logout behavior in Header.tsx, per the doc-as-you-go
    convention
  actor: logan
  at: '2026-09-16'
evidence:
- web/tests/unit/Header.test.tsx::Header (signed in) > clears session and navigates
  home on logout click
designated_repro_test: null
acceptance:
- text: given a signed-in header, when logout is clicked, then the session is cleared
    and the landing page shows
  evidence:
  - web/tests/unit/Header.test.tsx::Header (signed in) > clears session and navigates
    home on logout click
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
