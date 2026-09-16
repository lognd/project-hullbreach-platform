---
id: T-draft-f7b53aa6
title: Fix ruff import-order (I001) in conftest.py/test_build.py now that hullbreach_server.db
  is importable
state: queued
kind: bug
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
- tests/unit/conftest.py
- tests/system/test_build.py
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
found while working T-0006: landing src/hullbreach_server/db made the lazy imports in these test files resolve as first-party, changing ruff isort's grouping and failing 'ruff check' in CI (server (python) job on PR #10). Needs an import-order fix (ruff check --fix), not a logic change.