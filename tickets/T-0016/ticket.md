---
id: T-0016
title: POST /api/v1/auth/register with username, email, and password validation
state: in-progress
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0014
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/auth.py
- src/hullbreach_server/auth/schemas.py
- tests/unit/test_auth_register.py
- src/hullbreach_server/api/__init__.py
- pyproject.toml
- uv.lock
- tests/unit/test_roles.py
- docs/index.md
- design/hullbreach.strata
- docs/design/sprint-1.md
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: src/hullbreach_server/api/__init__.py
  reason: mount the new auth router onto api_router under /api/v1/auth, per docs/design/sprint-1.md
    section 5
  actor: logan
  at: '2026-09-16'
- op: add
  glob: pyproject.toml
  reason: add pydantic[email] extra for EmailStr validation on RegisterRequest, per
    docs/design/sprint-1.md section 5
  actor: logan
  at: '2026-09-16'
- op: add
  glob: uv.lock
  reason: add pydantic[email] extra for EmailStr validation on RegisterRequest, per
    docs/design/sprint-1.md section 5
  actor: logan
  at: '2026-09-16'
- op: add
  glob: tests/unit/test_roles.py
  reason: T-0016 implements RegisterRequest with no role field at all, which makes
    T-0028's pre-existing xfail(strict=True) test_role_is_never_accepted_as_an_input_field_on_register_schema
    an unexpected strict xpass; dropping only that test's xfail marker, no other T-0028
    test touched
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: add docs/index.md#auth-api section for register, and declare the api->logging
    Flow api/auth.py's module logger needs
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: add docs/index.md#auth-api section for register, and declare the api->logging
    Flow api/auth.py's module logger needs
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: add docs/index.md#auth-api section for register, and declare the api->logging
    Flow api/auth.py's module logger needs
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: add docs/index.md#auth-api section for register, and declare the api->logging
    Flow api/auth.py's module logger needs
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/sprint-1.md
  reason: AFFECT001 on the new f_api_to_logging flow needs its section-9 doc touched
  actor: logan
  at: '2026-09-16'
evidence:
- tests/unit/test_auth_register.py::test_register_duplicate_username_returns_409_with_field
- tests/unit/test_auth_register.py::test_register_valid_request_returns_201_with_player_defaults
designated_repro_test: null
acceptance:
- text: given a duplicate username, when registering, then 409 with a field-specific
    message
  evidence:
  - tests/unit/test_auth_register.py::test_register_duplicate_username_returns_409_with_field
- text: given a valid request, when registering, then 201 and role Player, currency
    0, rating default
  evidence:
  - tests/unit/test_auth_register.py::test_register_valid_request_returns_201_with_player_defaults
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---

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
