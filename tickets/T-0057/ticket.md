---
id: T-0057
title: RatingChange rows written on match record and exposed with the match
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0055
tier: ticket
sprint: sprint-2
runs_last: false
milestone: 0.2.0
flavour: null
due: null
rank: null
points: 2
unsized_ack: false
unsized_ack_reason: null
tokens_in: null
tokens_out: null
tokens_cache_read: null
usage: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
worktree: null
branch: null
scope:
- src/hullbreach_server/db/models/rating.py
- src/hullbreach_server/services/matches.py
- tests/unit/test_rating_history.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
triage_changes:
- field: points
  old_value: null
  new_value: '2'
  reason: ticket sizing
  actor: logan
  at: '2026-09-26'
designated_repro_test: null
acceptance:
- text: given a recorded match, when fetched, then before and after ratings for both
    players are present
  evidence: []
threat: null
component: null
labels:
- jira:SCRUM-141
- owner:lognd
anchor: false
anchor_reason: null
land_commit: null
---
