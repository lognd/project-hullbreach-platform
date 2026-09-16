---
id: T-draft-68a47ce3
title: Wire GET /api/v1/ready into a real caller (web/ops)
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
- web/src/**
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
found while working T-0012: the readiness route (GET /api/v1/ready) has no caller outside its own tests yet (WIRE001 waived on T-0012 pending this). Wire it into the web app's health/status check or ops tooling once one exists.