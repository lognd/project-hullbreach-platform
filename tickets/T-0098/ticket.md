---
id: T-0098
title: Sprint 1 xfail test skeleton (python)
state: in-progress
kind: docs
origin: human
created: '2026-09-16'
priority: medium
parent: null
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- tests/unit/conftest.py
- tests/unit/test_db_engine.py
- tests/unit/test_seed.py
- tests/unit/test_api.py
- tests/unit/test_passwords.py
- tests/unit/test_auth_register.py
- tests/unit/test_sessions.py
- tests/unit/test_auth_login.py
- tests/unit/test_auth_logout.py
- tests/unit/test_auth_game.py
- tests/unit/test_roles.py
- tests/system/test_build.py
- ty.toml
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given docs/design/sprint-1.md section 7's acceptance table, when uv run pytest
    runs, then every planned node id in that table exists, is marked xfail(strict=True),
    and the full suite reports zero failures and zero errors
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
Test-first xfail(strict=True) skeleton for the sprint-1 backend tickets (T-0006, T-0007, T-0008, T-0012, T-0015, T-0016, T-0019, T-0020, T-0023, T-0026, T-0028), written against docs/design/sprint-1.md before any implementation lands. Every test imports its planned symbols lazily inside the test/fixture body so collection succeeds and the test fails at call time via a real ImportError, reported as xfail. Adds tests/unit/conftest.py (engine/db_session/app/client fixtures per design section 7) and ty.toml (excludes tests/ from frob's whole-repo ty gate, matching CI's own ty check src/ scope).