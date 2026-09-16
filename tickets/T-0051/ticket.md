---
id: T-0051
title: S16 Record a finished match
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0050
tier: story
sprint: sprint-2
runs_last: false
milestone: 0.2.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/matches.py
- src/hullbreach_server/app/config.py
- src/hullbreach_server/auth/server_keys.py
- src/hullbreach_server/db/migrations/
- src/hullbreach_server/db/models/match.py
- src/hullbreach_server/services/matches.py
- tests/unit/test_match_models.py
- tests/unit/test_matches_record.py
- tests/unit/test_server_keys.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given an authenticated game server, when it submits a result once, then it
    is recorded; when it resubmits, then it is recognized and not double-counted
  evidence: []
- text: given an unauthenticated caller, when it submits a result, then it is rejected
  evidence: []
- text: given a recorded match, when either player's history is fetched within seconds,
    then it shows
  evidence: []
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
As a game server, I want to report a completed match with both players, the winner, duration, and per-player stats, so that the platform is the single source of truth for what happened.

Open questions:
- How does the game server authenticate: a server API key, or the players' own tokens?
- Which stats in v1: damage dealt, blocks destroyed, blocks placed mid-match, time alive?
- Idempotency: what if the server retries after a timeout?
