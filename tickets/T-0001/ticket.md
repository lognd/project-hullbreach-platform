---
id: T-0001
title: Scaffold the platform monorepo
state: in-progress
kind: feature
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
- src/**
- tests/**
- web/**
- docs/**
- '*'
- .github/**
- invariants/**
- tickets/**
scope_breadth_ack: true
scope_breadth_ack_reason: 'package-wide scaffold epic: the whole initial tree lands
  under this ticket'
no_scope_declared: false
no_scope_declared_reason: null
evidence:
- tests/system/test_build.py::test_package_imports
- tests/system/test_build.py::test_cli_help
designated_repro_test: null
acceptance:
- text: given a fresh clone, when uv sync and npm ci run, then frob check reports
    0 errors
  evidence:
  - tests/system/test_build.py::test_package_imports
  - tests/system/test_build.py::test_cli_help
- text: given create_app, when GET /api/v1/health, then 200 with status ok
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
