---
id: T-0095
title: Sprint 1 system design doc and strata model
state: done
kind: docs
origin: human
created: '2026-09-16'
priority: medium
parent: null
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- docs/design/sprint-1.md
- design/hullbreach.strata
- docs/design/registry/capability-via-ratchet.lock.json
- docs/index.md
- .prettierignore
- frob.toml
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: docs/design/registry/capability-via-ratchet.lock.json
  reason: capability-via-ratchet lock file and the docs/index.md link needed to link/discharge
    the strata model's own gate findings (REF001/002, SYS111)
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: capability-via-ratchet lock file and the docs/index.md link needed to link/discharge
    the strata model's own gate findings (REF001/002, SYS111)
  actor: logan
  at: '2026-09-16'
- op: add
  glob: .prettierignore
  reason: prettier chokes on design/*.strata and reformats the markdown doc without
    it; needed to make prettier --check clean for CI
  actor: logan
  at: '2026-09-16'
- op: add
  glob: frob.toml
  reason: needed a [[refs.entrypoint]] declaration for the capability-via-ratchet
    lock file (REF002)
  actor: logan
  at: '2026-09-16'
triage_changes:
- field: kind
  old_value: feature
  new_value: docs
  reason: 'docs-only design pass; cmd: evidence requires kind=docs/ux per COV003'
  actor: logan
  at: '2026-09-16'
evidence:
- cmd:grep -n 'module hullbreach_sprint1' design/hullbreach.strata exit=0 sha256=4619336c0007
kind_history:
- 2026-09-16 feature->docs evidence=1 done_report=yes
designated_repro_test: null
acceptance:
- text: given the sprint-1 tickets' thin bodies, when an implementer or test-writing
    agent reads docs/design/sprint-1.md, then they find a concrete spec (module map,
    data model, config, CLI, auth contracts, web routing, test-to-acceptance-criterion
    mapping) with no open question left unresolved or undocumented
  evidence:
  - cmd:grep -n 'module hullbreach_sprint1' design/hullbreach.strata exit=0 sha256=4619336c0007
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
Design-first pass for milestone 0.1.0: human spec plus strata kernel model of the planned modules and flows for T-0006, T-0007, T-0008, T-0010, T-0012, T-0015, T-0016, T-0017, T-0019, T-0020, T-0021, T-0023, T-0024, T-0026, T-0028, T-0044. No single epic covers both the database (E1) and auth (E2) tickets this design spans, so this ticket is filed with no parent epic.