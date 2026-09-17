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
