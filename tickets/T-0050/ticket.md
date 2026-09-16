---
id: T-0050
title: E5 Match records and ELO
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: high
parent: null
tier: epic
sprint: sprint-2
runs_last: false
milestone: 0.2.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- docs/index.md
- src/hullbreach_server/api/leaderboard.py
- src/hullbreach_server/api/matches.py
- src/hullbreach_server/api/me.py
- src/hullbreach_server/app/config.py
- src/hullbreach_server/auth/server_keys.py
- src/hullbreach_server/db/migrations/
- src/hullbreach_server/db/models/match.py
- src/hullbreach_server/db/models/rating.py
- src/hullbreach_server/rating/elo.py
- src/hullbreach_server/services/leaderboard.py
- src/hullbreach_server/services/matches.py
- tests/unit/test_elo.py
- tests/unit/test_leaderboard.py
- tests/unit/test_match_models.py
- tests/unit/test_matches_record.py
- tests/unit/test_me_matches.py
- tests/unit/test_rating_history.py
- tests/unit/test_server_keys.py
- web/src/pages/History.tsx
- web/src/pages/Leaderboard.tsx
- web/tests/unit/History.test.tsx
- web/tests/unit/Leaderboard.test.tsx
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
- S16 Record a finished match
- S17 Update ratings after a match
- S18 Browse my match history
- S19 See where I stand
