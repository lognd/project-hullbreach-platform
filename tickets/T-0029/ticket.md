---
id: T-0029
title: E3 Player profile
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: high
parent: null
tier: epic
sprint: sprint-2
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/me.py
- src/hullbreach_server/auth/sessions.py
- src/hullbreach_server/db/models/inventory.py
- src/hullbreach_server/services/account_deletion.py
- src/hullbreach_server/services/profile.py
- tests/unit/test_active_skin.py
- tests/unit/test_me.py
- tests/unit/test_me_delete.py
- tests/unit/test_me_edit.py
- web/src/components/SkinPicker.tsx
- web/src/pages/Profile.tsx
- web/src/pages/Settings.tsx
- web/tests/unit/Profile.test.tsx
- web/tests/unit/Settings.test.tsx
- web/tests/unit/SkinPicker.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
Epic from the Module 4 story map. Stories:
- S09 View my profile
- S10 Edit my account details
- S11 Delete my account
- S12 Equip a skin
