---
id: T-0030
title: S09 View my profile
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0029
tier: story
sprint: sprint-2
runs_last: false
milestone: 0.2.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/me.py
- src/hullbreach_server/services/profile.py
- tests/unit/test_me.py
- web/src/pages/Profile.tsx
- web/tests/unit/Profile.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a logged-in player, when they open their profile, then username, rating,
    currency, owned skins, and last five matches show
  evidence: []
- text: given a new match or purchase, when the profile loads, then it reflects the
    change without a code change or manual refresh of the database
  evidence: []
- text: given a phone-width screen, when the profile renders, then it is usable
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want a profile page that shows my username, rating, currency, owned skins, and recent matches, so that I can see how I am doing at a glance.

Open questions:
- Public profile by username, or private to the owner?
- How many recent matches before linking to full history?
