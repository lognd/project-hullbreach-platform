---
id: T-0001
title: Scaffold the platform monorepo
state: done
kind: feature
origin: human
created: '2026-09-15'
priority: high
parent: null
tier: ticket
sprint: null
runs_last: false
milestone: null
flavour: null
due: null
rank: null
points: null
unsized_ack: false
unsized_ack_reason: null
tokens_in: null
tokens_out: null
tokens_cache_read: null
usage: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
worktree: null
branch: null
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
- tests/system/test_build.py::test_app_builds_and_serves_health
- tests/unit/test_api.py::test_health_reports_ok_and_version
designated_repro_test: null
acceptance:
- text: given a fresh clone, when uv sync and npm ci run, then frob check reports
    0 errors
  evidence:
  - tests/system/test_build.py::test_package_imports
  - tests/system/test_build.py::test_cli_help
- text: given create_app, when GET /api/v1/health, then 200 with status ok
  evidence:
  - tests/system/test_build.py::test_app_builds_and_serves_health
  - tests/unit/test_api.py::test_health_reports_ok_and_version
threat: null
component: null
labels:
- jira:none
anchor: false
anchor_reason: null
land_commit: null
---
