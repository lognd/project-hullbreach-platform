---
id: T-draft-7d70b385
title: 'CI: restore coverage lock after refresh so main pushes stay clean'
state: queued
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
- tickets/**
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
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
