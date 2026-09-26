---
id: T-0060
title: Website match history page with paging
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0058
tier: ticket
sprint: sprint-2
runs_last: false
milestone: 0.2.0
flavour: null
due: null
rank: null
points: 3
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
- web/src/pages/History.tsx
- web/tests/unit/History.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
triage_changes:
- field: points
  old_value: null
  new_value: '3'
  reason: ticket sizing
  actor: logan
  at: '2026-09-26'
designated_repro_test: null
acceptance:
- text: given a page of matches, when load more is pressed, then the next page appends
  evidence: []
threat: null
component: null
labels:
- jira:SCRUM-144
- owner:a-carten
anchor: false
anchor_reason: null
land_commit: null
---
