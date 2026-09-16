---
id: T-0008
title: Seed command loading 100+ catalog items and the first admin account
state: in-progress
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0005
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/db/seed.py
- src/hullbreach_server/db/seed_items.json
- tests/unit/test_seed.py
- src/hullbreach_server/__main__.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: src/hullbreach_server/__main__.py
  reason: wiring the db seed subcommand requires replacing __main__.py's _db_seed
    stub (frob:todo T-0008) with the real dispatch to db/seed.py::seed
  actor: logan
  at: '2026-09-16'
evidence:
- tests/unit/test_seed.py::test_seed_creates_100_items_and_one_admin
- tests/unit/test_seed.py::test_seed_is_idempotent_on_second_run
designated_repro_test: null
acceptance:
- text: given an empty database, when seed runs, then item count >= 100 and one Administrator
    exists
  evidence:
  - tests/unit/test_seed.py::test_seed_creates_100_items_and_one_admin
- text: given a seeded database, when seed runs again, then nothing is duplicated
  evidence:
  - tests/unit/test_seed.py::test_seed_is_idempotent_on_second_run
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
