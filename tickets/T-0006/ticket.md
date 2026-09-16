---
id: T-0006
title: Database engine and session dependency from HULLBREACH_DATABASE_URL, fail fast
  at startup
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
- src/hullbreach_server/db/__init__.py
- src/hullbreach_server/db/engine.py
- tests/unit/test_db_engine.py
- docs/index.md
- pyproject.toml
- uv.lock
- design/hullbreach.strata
- docs/design/registry/capability-via-ratchet.lock.json
- docs/design/sprint-1.md
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: docs/index.md
  reason: T-0006 needs docs/index.md updates, sqlalchemy/psycopg deps, and the sprint-1
    strata model brought in sync with the landed db/engine.py surface
  actor: logan
  at: '2026-09-16'
- op: add
  glob: pyproject.toml
  reason: T-0006 needs docs/index.md updates, sqlalchemy/psycopg deps, and the sprint-1
    strata model brought in sync with the landed db/engine.py surface
  actor: logan
  at: '2026-09-16'
- op: add
  glob: uv.lock
  reason: T-0006 needs docs/index.md updates, sqlalchemy/psycopg deps, and the sprint-1
    strata model brought in sync with the landed db/engine.py surface
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: T-0006 needs docs/index.md updates, sqlalchemy/psycopg deps, and the sprint-1
    strata model brought in sync with the landed db/engine.py surface
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/registry/capability-via-ratchet.lock.json
  reason: T-0006 adds hullbreach_server_db's first 'sql' via-site (check_connectivity),
    which must bump the committed via-ratchet ceiling from 0 to 1
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/sprint-1.md
  reason: AFFECT001 requires the design doc's affects()-closure sections (7, 9) to
    be touched alongside the strata flows T-0006 adds/edits
  actor: logan
  at: '2026-09-16'
evidence:
- tests/unit/test_db_engine.py::test_check_connectivity_names_host_on_unreachable_url
- tests/unit/test_db_engine.py::test_check_connectivity_never_logs_the_full_url_with_password
- tests/unit/test_db_engine.py::test_check_connectivity_succeeds_on_reachable_sqlite_engine
- tests/unit/test_db_engine.py::test_create_db_engine_returns_a_sqlalchemy_engine
- tests/unit/test_db_engine.py::test_base_is_shared_across_db_package
- tests/unit/test_db_engine.py::test_base_metadata_has_naming_convention_for_alembic
- tests/unit/test_db_engine.py::test_get_db_dependency_yields_a_session
designated_repro_test: null
acceptance:
- text: given an unreachable database URL, when create_app starts, then startup fails
    with a message naming the host
  evidence:
  - tests/unit/test_db_engine.py::test_check_connectivity_names_host_on_unreachable_url
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
