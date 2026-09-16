---
id: T-0074
title: E7 Administration
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: high
parent: null
tier: epic
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/admin/items.py
- src/hullbreach_server/api/admin/matches.py
- src/hullbreach_server/api/admin/players.py
- src/hullbreach_server/api/admin/ratings.py
- src/hullbreach_server/api/auth.py
- src/hullbreach_server/db/models/moderation.py
- src/hullbreach_server/services/admin.py
- src/hullbreach_server/services/catalog.py
- src/hullbreach_server/services/matches.py
- tests/unit/test_admin_items.py
- tests/unit/test_admin_players.py
- tests/unit/test_admin_ratings.py
- tests/unit/test_admin_void.py
- tests/unit/test_moderation.py
- web/src/pages/admin/Items.tsx
- web/src/pages/admin/Players.tsx
- web/src/router.tsx
- web/tests/unit/AdminItems.test.tsx
- web/tests/unit/AdminPlayers.test.tsx
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
- S23 Look up and moderate a player
- S24 Correct a player's rating
- S25 Curate the item catalog
