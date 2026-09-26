---
id: T-draft-db8c7406
title: 'S01-5: Document the local Docker PostgreSQL setup and the hosted database
  switch in the README'
state: queued
kind: feature
origin: human
created: '2026-09-26'
priority: critical
parent: T-0005
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
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
- src/hullbreach_server/__main__.py
- src/hullbreach_server/db/__init__.py
- src/hullbreach_server/db/engine.py
- src/hullbreach_server/db/migrations/
- src/hullbreach_server/db/seed.py
- src/hullbreach_server/db/seed_items.json
- tests/system/test_build.py
- tests/unit/test_db_engine.py
- tests/unit/test_seed.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
threat: null
component: null
labels:
- infra
- platform
- jira:SCRUM-78
- owner:lognd
anchor: false
anchor_reason: null
land_commit: null
---
https://aliens-against-humanity.atlassian.net/browse/SCRUM-78

Document the local Docker PostgreSQL setup and the hosted database switch in the README
Parent story: SCRUM-22