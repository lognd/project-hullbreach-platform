---
id: T-0021
title: Website login page and persisted session across reloads
state: done
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
- web/src/api/auth.ts
- design/hullbreach.strata
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
- op: add
  glob: web/src/api/auth.ts
  reason: removing the WIRE001 waiver on login() now that Login.tsx calls it, and
    adding a frob:tests citation to Login.test.tsx
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: T-0021 implemented the login form/fetch call (web/src/api/auth.ts::login)
    without a request timeout; re-pointing the REL200:f_login_web waiver at T-0102
    (already filed for auth.ts's timeout follow-up) instead of this ticket
  actor: logan
  at: '2026-09-16'
evidence:
- web/tests/unit/Login.test.tsx::Login page > keeps user signed in after reload
designated_repro_test: null
acceptance:
- text: given a login, when the page reloads, then the user is still shown as signed
    in
  evidence:
  - web/tests/unit/Login.test.tsx::Login page > keeps user signed in after reload
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
