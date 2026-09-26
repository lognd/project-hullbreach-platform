---
id: T-0089
title: ShipDesign model and CRUD under /api/v1/me/designs storing the design as validated
  JSON
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0088
tier: ticket
sprint: sprint-2
runs_last: false
milestone: 0.2.0
flavour: null
due: null
rank: null
points: null
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
- src/hullbreach_server/db/models/design.py
- src/hullbreach_server/api/designs.py
- tests/unit/test_designs.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a design over the size limit, when saved, then 413 with the limit named
  evidence: []
threat: null
component: null
labels:
- needs-game
- jira:SCRUM-175
- owner:lognd
anchor: false
anchor_reason: null
land_commit: null
---
