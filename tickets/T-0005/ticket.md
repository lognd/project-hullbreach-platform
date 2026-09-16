---
id: T-0005
title: S01 Run the platform against a central database
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0004
tier: story
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
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
acceptance:
- text: given a connection string from env or config, when the API starts, then it
    connects, and refuses to start with a clear message if the database is unreachable
  evidence: []
- text: given two machines pointed at the same database, when both run the API, then
    they see the same data
  evidence: []
- text: given a fresh database, when the documented init command runs, then it has
    the current schema
  evidence: []
- text: given an initialized database, when the seed command runs, then at least 100
    catalog items and an admin account exist
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a developer, I want the API to read its database location from configuration and run against a PostgreSQL instance that is not on the same machine, so that the system meets the course requirement of multiple machines with a central database, and switching from a local to a hosted database is a settings change.

Open questions:
- Host a shared PostgreSQL for the team in Sprint 1, or Docker locally until the demo?
- Who owns schema migrations: hand-written SQL or Alembic?
- Seed strategy for the 100+ item dataset: checked-in SQL or a script?
