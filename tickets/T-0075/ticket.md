---
id: T-0075
title: S23 Look up and moderate a player
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0074
tier: story
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/admin/players.py
- src/hullbreach_server/api/auth.py
- src/hullbreach_server/db/models/moderation.py
- src/hullbreach_server/services/admin.py
- tests/unit/test_admin_players.py
- tests/unit/test_moderation.py
- web/src/pages/admin/Players.tsx
- web/src/router.tsx
- web/tests/unit/AdminPlayers.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a username or email, when an admin searches, then they see the profile,
    matches, and trust events
  evidence: []
- text: given a player, when an admin suspends them, then the player cannot log in
    and sees why; reinstate reverses it
  evidence: []
- text: given any moderation action, when performed, then admin, time, and reason
    are recorded
  evidence: []
- text: given a Player session, when any admin screen or endpoint is requested, then
    it is refused
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a administrator, I want to search for a player and suspend or reinstate their account, so that I can act on cheating or abuse reports.

Open questions:
- Suspension: time-boxed or indefinite? Does it block login, ranked play, or both?
- Record a reason and who did it?
