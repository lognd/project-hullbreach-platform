---
id: T-0008
title: Seed command loading 100+ catalog items and the first admin account
state: done
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
- src/hullbreach_server/auth/passwords.py
- docs/index.md
- design/hullbreach.strata
- docs/design/sprint-1.md
- .env.example
- docs/design/registry/capability-via-ratchet.lock.json
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
- op: add
  glob: src/hullbreach_server/auth/passwords.py
  reason: seed() now calls hash_password, making its WIRE001 waiver (follow_up=T-0016)
    stale; remove it
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: seed.py needs docs/index.md's public API/db-seed paragraph updated, a declared
    f_db_to_auth flow and fs.read capability in the strata model, a sprint-1.md note
    about the items-table runtime create, and .env.example's HULLBREACH_ADMIN_* documentation
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: seed.py needs docs/index.md's public API/db-seed paragraph updated, a declared
    f_db_to_auth flow and fs.read capability in the strata model, a sprint-1.md note
    about the items-table runtime create, and .env.example's HULLBREACH_ADMIN_* documentation
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/sprint-1.md
  reason: seed.py needs docs/index.md's public API/db-seed paragraph updated, a declared
    f_db_to_auth flow and fs.read capability in the strata model, a sprint-1.md note
    about the items-table runtime create, and .env.example's HULLBREACH_ADMIN_* documentation
  actor: logan
  at: '2026-09-16'
- op: add
  glob: .env.example
  reason: seed.py needs docs/index.md's public API/db-seed paragraph updated, a declared
    f_db_to_auth flow and fs.read capability in the strata model, a sprint-1.md note
    about the items-table runtime create, and .env.example's HULLBREACH_ADMIN_* documentation
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/registry/capability-via-ratchet.lock.json
  reason: seed.py's new fs.read/env.read call sites in hullbreach_server_db need the
    ratchet ceiling raised (SYS111)
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
