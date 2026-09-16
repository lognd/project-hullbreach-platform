---
id: T-0009
title: S02 Block merges that fail the quality gate
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0004
tier: story
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
- text: given a pull request with a failing check, when a non-bypass member tries
    to merge, then GitHub refuses
  evidence: []
- text: given the required check, when it runs, then it covers both the Python and
    TypeScript halves
  evidence: []
- text: given the README, when a teammate runs the gate locally, then they get the
    same result as CI
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a developer, I want every pull request to run lint, type checks, tests, and the design-system check before it can merge into main, so that a broken change never reaches the branch we demo from.

Open questions:
- Is frob a required status check from day one, or advisory while the team learns it?
- One approving review required, or is green CI enough for small changes?
