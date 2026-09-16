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

Evidence: tests/unit/test_db_engine.py::test_check_connectivity_names_host_on_unreachable_url
(bound to acceptance [1]), plus 6 more test_db_engine.py node ids bound
as flat evidence (never-logs-password, succeeds-on-reachable-sqlite,
returns-a-sqlalchemy-engine, base-is-shared, base-metadata-naming-
convention, get-db-yields-a-session). All 7 xfail(strict=True) stubs
pass with the xfail markers removed.

Filed: T-draft-696af73f (wire check_connectivity into App startup per
design decision D2; scope src/hullbreach_server/app/app.py,
tests/unit/test_app.py).

Gates: frob check --ticket T-0006 clean except two known structural
findings unrelated to this ticket's code: CROSSTICKET001/SCOPE001 on
tickets/T-0006/ticket.md and tickets/T-draft-696af73f/ticket.md, both
because T-0003's declared scope is 'tickets/**' and T-0003 is still
in-progress -- every ticket's own bookkeeping file collides with that
lease. `frob ticket land --allow-cross-ticket` is the documented
resolution; noted for the coordinator since it recurs for any ticket
filed/closed while T-0003 is open.
ruff check/format, ty check, and typani.lint all pass. Full unit suite
is green except tests/unit/test_auth_register.py::test_register_response_never_exposes_password_hash,
a pre-existing xpass(strict) failure on main (T-0016, out of this
ticket's scope) confirmed unrelated by running it on main before this
branch's changes.

### Changed
```
 tickets/T-0006/ticket.md           | 51 +++++++++++++++++++++++++++++++++++++-
 tickets/T-draft-696af73f/ticket.md | 30 ++++++++++++++++++++++
 2 files changed, 80 insertions(+), 1 deletion(-)
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
