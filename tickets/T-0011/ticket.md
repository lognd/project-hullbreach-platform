---
id: T-0011
title: S03 Confirm the API is alive
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
- src/hullbreach_server/api/health.py
- tests/unit/test_api.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given no credentials, when GET /api/v1/health is called, then 200 with the
    running version
  evidence: []
- text: given a local machine, when the endpoint is called, then it answers in under
    100 ms
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a game server, I want an unauthenticated endpoint that reports the API is up and which version it is, so that I can refuse to start a match when the platform is unreachable instead of losing results later.

Open questions:
- Should health also report database connectivity, or stay a pure liveness probe with a separate readiness endpoint?
