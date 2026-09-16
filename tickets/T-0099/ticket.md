---
id: T-0099
title: Wire check_connectivity into App startup for fail-fast DB check
state: queued
kind: feature
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
- src/hullbreach_server/app/app.py
- tests/unit/test_app.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
found while working T-0006: create_db_engine/check_connectivity exist per design D2, but App.__call__ does not call check_connectivity before uvicorn.run yet. This ticket wires that call and adds the test for it (docs/design/sprint-1.md section 3, decision D2).