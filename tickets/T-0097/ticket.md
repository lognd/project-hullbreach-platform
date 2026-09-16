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
designated_repro_test: null
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
found while working T-0096: the design's 'tests' node (design/hullbreach.strata) only globs 'tests/**', so web/tests/unit/*.test.tsx's observed client_storage capability (localStorage use in Header.test.tsx and Login.test.tsx) is unbound, tripping SELFAUDIT001/SYS103. Widen the node's code= glob (or add a second node) to also cover web/tests/**.