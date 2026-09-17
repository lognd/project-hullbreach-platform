---
id: T-0020
title: POST /api/v1/auth/login issuing a token, with failed-login rate limiting
state: in-progress
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0018
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/auth.py
- tests/unit/test_auth_login.py
- src/hullbreach_server/auth/sessions.py
- .env.example
- src/hullbreach_server/auth/schemas.py
- src/hullbreach_server/auth/passwords.py
- tests/unit/test_auth_game.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: src/hullbreach_server/auth/sessions.py
  reason: 'the failed-login rate limiter''s in-process store lives in auth/sessions.py
    per docs/design/sprint-1.md section 5 ("Store: ... behind a module-level lock
    in auth/sessions.py"); tests/unit/test_auth_login.py::test_rate_limit_window_resets_after_60_seconds
    monkeypatches hullbreach_server.auth.sessions.datetime directly, which only works
    if the limiter''s clock calls resolve through this module'
  actor: logan
  at: '2026-09-16'
- op: add
  glob: .env.example
  reason: document HULLBREACH_LOGIN_RATE_LIMIT_MAX and HULLBREACH_LOGIN_RATE_LIMIT_WINDOW_SECONDS,
    per docs/design/sprint-1.md section 3, brief-allowed config exception
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/auth/schemas.py
  reason: add LoginRequest/LoginResponse pydantic schemas for POST /api/v1/auth/login,
    matching web/src/api/auth.ts's existing types
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/auth/passwords.py
  reason: login now calls verify_password, resolving its WIRE001 waiver that named
    T-0020 as follow_up; remove the now-satisfied waiver
  actor: logan
  at: '2026-09-16'
- op: add
  glob: tests/unit/test_auth_game.py
  reason: T-0020's working login makes _register_and_login succeed, so this pre-existing
    xfail(strict=True) test now reaches a real 404 from GET /session (T-0026, not
    yet implemented) whose body incidentally satisfies this test's weak 'field absent'
    assertions, turning it into a strict xpass; dropping only this one marker, the
    other three T-0026 xfail tests in this file are untouched and still correctly
    fail
  actor: logan
  at: '2026-09-16'
evidence:
- tests/unit/test_auth_login.py::test_sixth_failed_login_attempt_in_window_returns_429
designated_repro_test: null
acceptance:
- text: given five failed attempts in a minute, when a sixth arrives, then 429
  evidence:
  - tests/unit/test_auth_login.py::test_sixth_failed_login_attempt_in_window_returns_429
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
