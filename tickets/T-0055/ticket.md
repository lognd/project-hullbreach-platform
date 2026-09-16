---
id: T-0055
title: S17 Update ratings after a match
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
- docs/index.md
- src/hullbreach_server/db/models/rating.py
- src/hullbreach_server/rating/elo.py
- src/hullbreach_server/services/matches.py
- tests/unit/test_elo.py
- tests/unit/test_rating_history.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a recorded match, when ratings update, then both change according to
    the documented formula
  evidence: []
- text: given any match, when ratings update, then the winner never loses rating and
    the loser never gains
  evidence: []
- text: given a rating change, when stored, then it is attached to the match so history
    can be reconstructed
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want my rating to go up when I beat a stronger opponent and down less when I lose to one, so that the number reflects skill and not just play count.

Open questions:
- Plain Elo with a fixed K-factor, or a higher K for new accounts?
- Starting rating and floor?
- Do unranked / LAN matches affect rating? (Proposal: only matches on a trusted game server do.)
