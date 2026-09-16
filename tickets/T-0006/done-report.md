## Done report

Changed:
- src/hullbreach_server/db/engine.py::Base
- src/hullbreach_server/db/engine.py::DatabaseError
- src/hullbreach_server/db/engine.py::create_db_engine
- src/hullbreach_server/db/engine.py::check_connectivity
- src/hullbreach_server/db/__init__.py::get_engine
- src/hullbreach_server/db/__init__.py::get_sessionmaker
- src/hullbreach_server/db/__init__.py::get_db
- design/hullbreach.strata (db node: may "sql", waiver wording refresh;
  new measured flows f_db_to_app, f_db_to_logging, f_tests_to_db)
- docs/design/registry/capability-via-ratchet.lock.json (db::sql baseline)
- docs/index.md, docs/design/sprint-1.md (doc anchors for the above)
- pyproject.toml / uv.lock (sqlalchemy, psycopg[binary])
- tests/unit/conftest.py, tests/system/test_build.py: ruff import-order
  (I001) fix -- landing db/ made these lazy imports resolve as
  first-party, which flipped isort's grouping in CI
- tests/unit/test_auth_register.py::test_register_response_never_exposes_password_hash:
  added an explicit `assert response.status_code == 201` before the body
  assertions, so it cannot XPASS on the current 404 (route not
  implemented until T-0016) -- it now xfails for the right reason again

Evidence: tests/unit/test_db_engine.py::test_check_connectivity_names_host_on_unreachable_url
(bound to acceptance [1]), plus 6 more test_db_engine.py node ids bound
as flat evidence (never-logs-password, succeeds-on-reachable-sqlite,
returns-a-sqlalchemy-engine, base-is-shared, base-metadata-naming-
convention, get-db-yields-a-session). All 7 xfail(strict=True) stubs
pass with the xfail markers removed. Full suite green locally
(`uv run pytest tests/ -n auto --cov=src --cov-report=term-missing`:
23 passed, 51 xfailed, 96% coverage on touched modules) and via
`frob coverage --full` (no DEGRADED warning).

Filed: T-0099 (was T-draft-696af73f; wire check_connectivity into App
startup per design decision D2). T-draft-f7b53aa6 and T-draft-8d975dbc
(filed for the two ripple issues above) were dropped per coordinator
direction once fixed directly in this ticket instead.

Gates: frob check --ticket T-0006 clean except CROSSTICKET001/SCOPE001
on tickets/T-0006/{ticket,done-report}.md, tickets/T-0099/ticket.md, and
the two now-dropped draft tickets' files -- all because T-0003's
declared scope is 'tickets/**' and T-0003 is still in-progress, so every
ticket's own bookkeeping file collides with that lease. This is
structural (any ticket filed/closed while T-0003 is open hits it), not
caused by this ticket's code; flagged for the coordinator since
`frob check --base origin/main --ticket T-0006` (the exact CI
invocation) exits 1 on it.
ruff check/format, ty check, and typani.lint all pass. `uv run pytest
tests/ -n auto --cov=src --cov-report=term-missing` (the exact CI
server-job command) is green.

### Changed
```
 design/hullbreach.strata                           |  34 +++-
 .../registry/capability-via-ratchet.lock.json      |   5 +
 docs/design/sprint-1.md                            |  11 +-
 docs/index.md                                      |  18 ++
 frob-coverage.lock.json                            |   4 +-
 pyproject.toml                                     |   2 +
 src/hullbreach_server/db/__init__.py               |  73 ++++++++
 src/hullbreach_server/db/engine.py                 |  95 ++++++++++
 tests/unit/test_db_engine.py                       |  24 +--
 tickets/T-0006/done-report.md                      |  60 +++++++
 tickets/T-0006/ticket.md                           | 124 ++++++++++++-
 tickets/T-0099/ticket.md                           |  30 ++++
 tickets/T-draft-8d975dbc/ticket.md                 |  33 ++++
 tickets/T-draft-f7b53aa6/ticket.md                 |  34 ++++
 uv.lock                                            | 193 +++++++++++++++++++++
 15 files changed, 715 insertions(+), 25 deletions(-)
```

### Evidence
- `tests/unit/test_db_engine.py::test_check_connectivity_names_host_on_unreachable_url` (pytest node id, verified passing when recorded)
- `tests/unit/test_db_engine.py::test_check_connectivity_never_logs_the_full_url_with_password` (pytest node id, verified passing when recorded)
- `tests/unit/test_db_engine.py::test_check_connectivity_succeeds_on_reachable_sqlite_engine` (pytest node id, verified passing when recorded)
- `tests/unit/test_db_engine.py::test_create_db_engine_returns_a_sqlalchemy_engine` (pytest node id, verified passing when recorded)
- `tests/unit/test_db_engine.py::test_base_is_shared_across_db_package` (pytest node id, verified passing when recorded)
- `tests/unit/test_db_engine.py::test_base_metadata_has_naming_convention_for_alembic` (pytest node id, verified passing when recorded)
- `tests/unit/test_db_engine.py::test_get_db_dependency_yields_a_session` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 7 passed (from 7 evidence id(s))
- gates: unmeasured (no parsable gate-summary from a fresh check)
