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
- docs/index.md
- design/hullbreach.strata
- docs/design/sprint-1.md
- docs/design/registry/capability-via-ratchet.lock.json
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
- op: add
  glob: docs/index.md
  reason: document POST /auth/login in the Auth API section, and declare the env.read
    capability on hullbreach_server_auth for the two new rate-limit env var readers
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: document POST /auth/login in the Auth API section, and declare the env.read
    capability on hullbreach_server_auth for the two new rate-limit env var readers
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/sprint-1.md
  reason: AFFECT001 needs section-9 doc touched for the env.read capability grant
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/registry/capability-via-ratchet.lock.json
  reason: 'SYS111 ratchet: hullbreach_server_auth''s env.read via-list grew from 1
    to 3 sites with the two new rate-limit env readers'
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

## Done report

Changed:
src/hullbreach_server/api/auth.py::login
src/hullbreach_server/auth/schemas.py::LoginRequest
src/hullbreach_server/auth/schemas.py::LoginResponse
src/hullbreach_server/auth/sessions.py::current_time
src/hullbreach_server/auth/sessions.py::is_login_rate_limited
src/hullbreach_server/auth/sessions.py::record_failed_login
src/hullbreach_server/auth/sessions.py::clear_failed_logins
.env.example (HULLBREACH_LOGIN_RATE_LIMIT_MAX/_WINDOW_SECONDS)
docs/index.md (Auth API section extended for login)
design/hullbreach.strata (env.read via-list widened; REL200 waivers
  f_api_to_auth/session_token__issue/f_session_token_to_browser
  re-pointed to T-0100)
docs/design/sprint-1.md (section 9 note for the widened env.read grant)
docs/design/registry/capability-via-ratchet.lock.json
  (hullbreach_server_auth::env.read accepted_count 1 -> 3)

Evidence:
tests/unit/test_auth_login.py::test_login_valid_credentials_returns_200_with_token_and_user
tests/unit/test_auth_login.py::test_login_wrong_password_returns_401
tests/unit/test_auth_login.py::test_login_unknown_username_returns_the_same_401_message_as_wrong_password
tests/unit/test_auth_login.py::test_sixth_failed_login_attempt_in_window_returns_429
tests/unit/test_auth_login.py::test_successful_login_clears_the_failed_attempt_counter
tests/unit/test_auth_login.py::test_rate_limit_window_resets_after_60_seconds
tests/unit/test_auth_login.py::test_login_password_min_length_still_enforced_by_schema

Filed: none

Gates: frob check --base origin/main --ticket T-0020 clean, 0 errors.
ruff, ruff format, ty, full pytest (64 passed, 11 xfailed), frob
coverage --fail-on-degraded all clean.

Notes:
- The rate limiter's clock is read exactly once per HTTP request
  (auth/sessions.py::current_time), threaded through
  is_login_rate_limited/record_failed_login, because
  test_rate_limit_window_resets_after_60_seconds monkeypatches
  auth.sessions.datetime with a finite iterator of frozen instants --
  the limiter needed to live in auth/sessions.py (not a separate
  ratelimit.py) for that monkeypatch to reach it, and needed exactly
  one clock read per request to match the test's 6-value iterator.
- Added an autouse fixture in tests/unit/test_auth_login.py to clear
  the module-level `_failed_attempts` store between tests, since it is
  deliberately process-global (single-instance rate limiting) and
  every test in that file reuses the same username.
- Removed the now-satisfied WIRE001 waivers on issue_session
  (auth/sessions.py) and verify_password (auth/passwords.py); a route
  calls both now.
- Dropped the stale strict xfail on
  tests/unit/test_auth_game.py::test_session_endpoint_omits_username_and_email:
  T-0020's working login makes _register_and_login succeed, so this
  test now reaches a real 404 from GET /session (T-0026, not yet
  implemented) whose body incidentally satisfies its weak
  field-absence assertions, turning it into a strict xpass. The other
  three T-0026 xfail tests in that file are untouched and still
  correctly fail.
