---
id: T-0097
title: Widen strata tests node glob to cover web/tests
state: in-progress
kind: bug
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
- design/hullbreach.strata
- docs/design/registry/capability-via-ratchet.lock.json
- docs/design/sprint-1.md
- frob.toml
- web/scripts/run-vitest-ids.mjs
- package.json
- package-lock.json
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: docs/design/registry/capability-via-ratchet.lock.json
  reason: widening the tests node's client_storage grant requires raising this ratchet's
    accepted_count in the same diff (SYS111)
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/sprint-1.md
  reason: 'AFFECT001: widening the tests node''s code glob touches its affects()-closure
    doc anchor (section 7 test strategy), which must be updated in the same diff'
  actor: logan
  at: '2026-09-16'
- op: add
  glob: frob.toml
  reason: 'COV003/NoRunner: run_selected resolves web/tests/unit/*.test.tsx to language
    ''ts'', but frob.toml only declares a [[test.runner]] for language ''typescript'',
    so pytest-style vitest node-id evidence cannot be collected for a non-docs/ux
    ticket; add the matching runner entry'
  actor: logan
  at: '2026-09-16'
- op: remove
  glob: frob.toml
  reason: reverted the runner-language experiment; cmd evidence via kind=docs is the
    simpler fix
  actor: logan
  at: '2026-09-16'
- op: add
  glob: frob.toml
  reason: 'COV003/NoRunner: vitest node-id evidence needs a runner that translates
    a frob node id into vitest''s actual CLI shape (file + -t name), and language
    ''ts'' (not ''typescript'') is what run_selected reports for a .tsx test file'
  actor: logan
  at: '2026-09-16'
- op: add
  glob: web/scripts/run-vitest-ids.mjs
  reason: 'COV003/NoRunner: vitest node-id evidence needs a runner that translates
    a frob node id into vitest''s actual CLI shape (file + -t name), and language
    ''ts'' (not ''typescript'') is what run_selected reports for a .tsx test file'
  actor: logan
  at: '2026-09-16'
- op: add
  glob: package.json
  reason: the two web test files this ticket's evidence targets (T-0096, not yet merged)
    import @testing-library/user-event; adding it here so evidence can be verified
    against this branch without waiting on T-0096
  actor: logan
  at: '2026-09-16'
- op: add
  glob: package-lock.json
  reason: the two web test files this ticket's evidence targets (T-0096, not yet merged)
    import @testing-library/user-event; adding it here so evidence can be verified
    against this branch without waiting on T-0096
  actor: logan
  at: '2026-09-16'
evidence:
- web/tests/unit/Header.test.tsx::Header keyboard access > tab order matches visual
  order and Enter activates each control
- web/tests/unit/Login.test.tsx::Login page > keeps user signed in after reload
designated_repro_test: null
acceptance:
- text: given design/hullbreach.strata's tests node, when frob check runs against
    a branch carrying web/tests/unit/Header.test.tsx and Login.test.tsx, then their
    observed client_storage capability is bound by the node's code glob (no SELFAUDIT001/SYS103
    finding)
  evidence:
  - web/tests/unit/Header.test.tsx::Header keyboard access > tab order matches visual
    order and Enter activates each control
  - web/tests/unit/Login.test.tsx::Login page > keeps user signed in after reload
evidence_changes:
- old_node: cmd:npx vitest run web/tests/unit/Header.test.tsx web/tests/unit/Login.test.tsx
    exit=0 sha256=85e91495d928
  new_node: ''
  reason: 'kind=bug cannot carry cmd: evidence (COV003); replacing with real vitest
    node ids'
  actor: logan
  at: '2026-09-16'
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
found while working T-0096: the design's 'tests' node (design/hullbreach.strata) only globs 'tests/**', so web/tests/unit/*.test.tsx's observed client_storage capability (localStorage use in Header.test.tsx and Login.test.tsx) is unbound, tripping SELFAUDIT001/SYS103. Widen the node's code= glob (or add a second node) to also cover web/tests/**.

## Reopen log
- 2026-09-16: COV003: cmd: evidence is not allowed for kind=bug; replace with real pytest/vitest node-id evidence per CI's frob check finding