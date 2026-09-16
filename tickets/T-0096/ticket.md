---
id: T-0096
title: Sprint 1 failing test skeleton (web)
state: queued
kind: docs
origin: human
created: '2026-09-16'
priority: medium
parent: null
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- web/tests/unit/Header.test.tsx
- web/tests/unit/Register.test.tsx
- web/tests/unit/Login.test.tsx
- package.json
- package-lock.json
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
evidence:
- cmd:npx vitest run web/tests/unit/Header.test.tsx web/tests/unit/Register.test.tsx
  web/tests/unit/Login.test.tsx exit=0 sha256=f306fed9ad13
designated_repro_test: null
acceptance:
- text: given the sprint-1 web ticket bodies, when the failing-test skeleton is run,
    then vitest reports every planned it.fails node id passing (expected-fail) with
    no accidental xpass
  evidence:
  - cmd:npx vitest run web/tests/unit/Header.test.tsx web/tests/unit/Register.test.tsx
    web/tests/unit/Login.test.tsx exit=0 sha256=f306fed9ad13
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
Test-first failing-test skeleton (vitest it.fails) for the sprint-1 web tickets T-0044, T-0017, T-0021, T-0024, per docs/design/sprint-1.md section 7. Adds @testing-library/user-event as a devDependency for keyboard/click interaction in the header tab-order test.

## Reopen log
- 2026-09-16: SELFAUDIT001/SYS100: now that Header.test.tsx and Login.test.tsx exist on this branch, the tests node's client_storage capability is observed but not declared -- add the may via grants T-0097 deferred