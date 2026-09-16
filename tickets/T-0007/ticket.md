---
id: T-0007
title: Alembic migrations with a hullbreach_server db upgrade command
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
- src/hullbreach_server/db/migrations/
- src/hullbreach_server/__main__.py
- tests/system/test_build.py
- alembic.ini
- pyproject.toml
- uv.lock
- docs/index.md
- design/hullbreach.strata
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: alembic.ini
  reason: alembic.ini is the alembic config file this ticket needs (config-file exception);
    pyproject.toml/uv.lock gain the alembic dependency; docs/index.md needs syncing
    for the new __main__.py db subcommand
  actor: logan
  at: '2026-09-16'
- op: add
  glob: pyproject.toml
  reason: alembic.ini is the alembic config file this ticket needs (config-file exception);
    pyproject.toml/uv.lock gain the alembic dependency; docs/index.md needs syncing
    for the new __main__.py db subcommand
  actor: logan
  at: '2026-09-16'
- op: add
  glob: uv.lock
  reason: alembic.ini is the alembic config file this ticket needs (config-file exception);
    pyproject.toml/uv.lock gain the alembic dependency; docs/index.md needs syncing
    for the new __main__.py db subcommand
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: alembic.ini is the alembic config file this ticket needs (config-file exception);
    pyproject.toml/uv.lock gain the alembic dependency; docs/index.md needs syncing
    for the new __main__.py db subcommand
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: must re-point REL200 waivers on database_url__issue/revoke, f_database_url_to_db,
    and f_db_to_postgres away from T-0007 (which does not address strata-declared
    timeout attrs) before closing, per frob's LiveTrackerCited check
  actor: logan
  at: '2026-09-16'
evidence:
- tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
designated_repro_test: null
acceptance:
- text: given a fresh database, when the upgrade command runs, then alembic heads
    match the models
  evidence:
  - tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
