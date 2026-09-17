---
id: T-0010
title: Require one approving review and All checks pass in branch protection; document
  it
state: done
kind: docs
origin: human
created: '2026-09-15'
priority: medium
parent: T-0009
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- CONTRIBUTING.md
- README.md
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
triage_changes:
- field: kind
  old_value: feature
  new_value: docs
  reason: acceptance criterion is a GitHub branch-protection UI setting, not code
    -- no pytest/vitest node id exists to bind as evidence; cmd evidence (the docs-kind
    escape hatch) verifies the actual gh api ruleset state instead
  actor: logan
  at: '2026-09-16'
evidence:
- cmd:gh api repos/lognd/project-hullbreach-platform/rules/branches/main exit=0 sha256=df8956df9a54
kind_history:
- 2026-09-16 feature->docs evidence=0 done_report=yes
designated_repro_test: null
acceptance:
- text: given branch protection, when a PR has green CI but no approval, then merge
    is blocked for non-bypass members
  evidence:
  - cmd:gh api repos/lognd/project-hullbreach-platform/rules/branches/main exit=0
    sha256=df8956df9a54
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
