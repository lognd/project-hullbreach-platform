---
id: T-0028
title: Role enum on User, require_admin dependency returning 403, and role excluded
  from register/profile schemas
state: in-progress
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0027
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/db/models/user.py
- src/hullbreach_server/auth/deps.py
- src/hullbreach_server/auth/schemas.py
- tests/unit/test_roles.py
- docs/index.md
- src/hullbreach_server/db/migrations/versions/*.py
- src/hullbreach_server/db/models/session.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: docs/index.md
  reason: document require_admin in the Public API section
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/db/migrations/versions/*.py
  reason: re-point the permanent Alembic-reflection/TypeDecorator WIRE001 waivers
    that named T-0028 as follow_up to T-0100, since no ticket can ever statically
    wire them and T-0028 is closing
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/db/models/session.py
  reason: re-point the permanent Alembic-reflection/TypeDecorator WIRE001 waivers
    that named T-0028 as follow_up to T-0100, since no ticket can ever statically
    wire them and T-0028 is closing
  actor: logan
  at: '2026-09-16'
evidence:
- tests/unit/test_roles.py::test_player_token_on_admin_route_returns_403_with_permissions_message
designated_repro_test: null
acceptance:
- text: given a Player token, when an admin route is called, then 403 with a permissions
    message
  evidence:
  - tests/unit/test_roles.py::test_player_token_on_admin_route_returns_403_with_permissions_message
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---

## Done report

Changed:
src/hullbreach_server/auth/deps.py::require_admin
docs/index.md (require_admin documented in Public API section)

Choice for the admin-only route needed by the test suite: used the
existing test-only router (`_mount_admin_route` in
tests/unit/test_roles.py, already present in the pre-written test
skeleton), not a new minimal production route. No admin-facing route
exists anywhere in the milestone 0.1.0 design (admin moderation is a
later milestone per docs/index.md's own overview), so a real route
would have been invented scope, not something the design calls for.

Evidence:
tests/unit/test_roles.py::test_role_enum_has_exactly_player_and_admin_members
tests/unit/test_roles.py::test_user_default_role_is_player
tests/unit/test_roles.py::test_player_token_on_admin_route_returns_403_with_permissions_message
tests/unit/test_roles.py::test_admin_token_on_admin_route_returns_200
tests/unit/test_roles.py::test_role_is_never_accepted_as_an_input_field_on_register_schema
tests/unit/test_roles.py::test_missing_admin_route_dependency_never_returns_401_for_a_valid_player

Filed: none

Gates: frob check --base origin/main --ticket T-0028 clean, 0 errors.
ruff, ruff format, ty, full pytest (every sprint-1 xfail test now
passes with 0 remaining xfails in the suite), frob coverage
--fail-on-degraded all clean.

Notes:
- Role enum (player/admin) and the User model's default role landed
  with T-0015 -- verified unchanged, no code needed there.
- Waived WIRE001 on require_admin: no production admin route exists in
  0.1.0, follow_up="T-0076" (the first real admin route, milestone
  0.3.0).
- Re-pointed the migration files' and Session TypeDecorator's
  permanent Alembic-reflection WIRE001 waivers (which named T-0028 as
  follow_up) to T-0100, since no ticket can ever statically wire them
  and T-0028 is closing.
- This was the last sprint-1 (milestone 0.1.0) ticket; the full test
  suite now has zero xfail markers remaining.
