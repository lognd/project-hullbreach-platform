---
id: T-0010
title: Require one approving review and All checks pass in branch protection; document
  it
state: queued
kind: feature
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
designated_repro_test: null
acceptance:
- text: given branch protection, when a PR has green CI but no approval, then merge
    is blocked for non-bypass members
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
