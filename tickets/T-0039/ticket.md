---
id: T-0039
title: S12 Equip a skin
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0029
tier: story
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/me.py
- src/hullbreach_server/db/models/inventory.py
- tests/unit/test_active_skin.py
- web/src/components/SkinPicker.tsx
- web/src/pages/Profile.tsx
- web/tests/unit/SkinPicker.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given owned skins, when one is selected as active, then it saves; given an
    unowned skin, then refused
  evidence: []
- text: given an active skin, when the next match starts, then both players see it
    on the ship
  evidence: []
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want to choose which owned skin my ship uses, so that my ship looks the way I want in every match.

Open questions:
- Per-ship, per-block-type, or one ship-wide palette?
- Chosen on the website only, in the game only, or both?
