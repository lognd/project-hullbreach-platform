## Done report

Changed:
src/hullbreach_server/api/auth.py::register
src/hullbreach_server/api/auth.py::_duplicate_field
src/hullbreach_server/api/__init__.py (mount auth_router under /api/v1/auth)
src/hullbreach_server/auth/schemas.py::RegisterRequest
src/hullbreach_server/auth/schemas.py::UserProfile
src/hullbreach_server/auth/schemas.py::UserProfile.from_user
pyproject.toml / uv.lock (pydantic[email] extra for EmailStr)
docs/index.md (new "Auth API" section under Public API)
design/hullbreach.strata (f_api_to_logging flow)
docs/design/sprint-1.md (section 9 note for f_api_to_logging)

Evidence:
tests/unit/test_auth_register.py::test_register_valid_request_returns_201_with_player_defaults
tests/unit/test_auth_register.py::test_register_duplicate_username_returns_409_with_field
tests/unit/test_auth_register.py::test_register_duplicate_email_returns_409_with_field
tests/unit/test_auth_register.py::test_register_password_too_short_returns_422
tests/unit/test_auth_register.py::test_register_malformed_email_returns_422
tests/unit/test_auth_register.py::test_register_role_field_is_never_accepted_as_input
tests/unit/test_auth_register.py::test_register_response_never_exposes_password_hash

Filed: none

Gates: frob check --base origin/main --ticket T-0016 clean, 0 errors.
ruff, ruff format, ty, full pytest (56 passed, 19 xfailed), frob coverage
--fail-on-degraded all clean.

Also dropped the stale strict xfail on
tests/unit/test_roles.py::test_role_is_never_accepted_as_an_input_field_on_register_schema
(T-0028's file, out of T-0016's original scope, added with a reason):
T-0016's RegisterRequest has no `role` field at all, which makes that
one pre-existing assertion trivially true and turns the strict xfail
into a failing strict xpass; no other T-0028 test touched.
