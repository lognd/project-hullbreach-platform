---
id: T-0002
title: 'CI: restore coverage lock after refresh so main pushes stay clean'
state: in-progress
kind: bug
origin: human
created: '2026-09-15'
priority: high
parent: null
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- .github/workflows/ci.yml
- src/hullbreach_server/api/health.py
- src/hullbreach_server/logging/filter.py
- src/hullbreach_server/logging/formatter.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: src/hullbreach_server/api/health.py
  reason: drop the WIRE001 waivers that cite T-0001 so it can close
  actor: logan
  at: '2026-09-15'
- op: add
  glob: src/hullbreach_server/logging/filter.py
  reason: drop the WIRE001 waivers that cite T-0001 so it can close
  actor: logan
  at: '2026-09-15'
- op: add
  glob: src/hullbreach_server/logging/formatter.py
  reason: drop the WIRE001 waivers that cite T-0001 so it can close
  actor: logan
  at: '2026-09-15'
- op: remove
  glob: tickets/**
  reason: the CI fix only touches the workflow and three source files; the tickets
    glob made every later ticket look like T-0002 work (CROSSTICKET001)
  actor: logan
  at: '2026-09-15'
designated_repro_test: null
acceptance:
- text: given a push to main, when the frob check job runs, then PRE001/SCOPE001 do
    not fire
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
