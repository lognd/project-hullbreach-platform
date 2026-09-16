---
id: T-0027
title: S08 Distinguish administrators from players
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0013
tier: story
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/auth/deps.py
- src/hullbreach_server/auth/schemas.py
- src/hullbreach_server/db/models/user.py
- tests/unit/test_roles.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given any account, when inspected, then it has exactly one role, Player or
    Administrator
  evidence: []
- text: given an admin-only endpoint, when a Player session calls it, then 403 with
    a permissions error
  evidence: []
- text: given the register and profile-edit paths, when a role is supplied, then it
    is ignored or refused
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a administrator, I want my account to carry an Administrator role that ordinary accounts cannot grant themselves, so that moderation actions are only available to the team.

Open questions:
- How is the first admin created: seed script, environment variable, or database promotion?
- Can an admin promote other admins from the UI, or only via seed?
