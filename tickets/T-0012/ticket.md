---
id: T-0012
title: Readiness endpoint reporting database connectivity alongside the liveness health
  route
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0011
tier: ticket
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
evidence:
- tests/unit/test_api.py::test_ready_returns_200_when_database_reachable
- tests/unit/test_api.py::test_ready_returns_503_when_database_unreachable
designated_repro_test: null
acceptance:
- text: given a reachable database, when GET /api/v1/ready is called, then 200; when
    unreachable, then 503
  evidence:
  - tests/unit/test_api.py::test_ready_returns_200_when_database_reachable
  - tests/unit/test_api.py::test_ready_returns_503_when_database_unreachable
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
