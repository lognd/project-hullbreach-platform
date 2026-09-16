---
id: T-0007
title: Alembic migrations with a hullbreach_server db upgrade command
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0005
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/db/migrations/
- src/hullbreach_server/__main__.py
- tests/system/test_build.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a fresh database, when the upgrade command runs, then alembic heads
    match the models
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
