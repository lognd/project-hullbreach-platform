---
id: T-0028
title: Role enum on User, require_admin dependency returning 403, and role excluded
  from register/profile schemas
state: done
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
