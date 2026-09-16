---
id: T-0022
title: S06 Log out
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
- src/hullbreach_server/api/auth.py
- tests/unit/test_auth_logout.py
- web/src/components/Header.tsx
- web/tests/unit/Header.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a logged-in player, when they log out from any page, then they land
    on the landing page
  evidence: []
- text: given a logout, when the previous token is used, then the API rejects it
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want to log out from any page, so that the next person at this computer cannot act as me.

Open questions:
- Log out of this device only, or all devices?
