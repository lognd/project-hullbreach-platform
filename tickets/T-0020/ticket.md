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
