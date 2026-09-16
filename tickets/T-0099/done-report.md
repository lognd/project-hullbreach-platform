## Done report

Wired check_connectivity into App startup per docs/design/sprint-1.md
section 3 decision D2: App.__call__ now builds an engine from
AppConfig.database_url and runs check_connectivity before uvicorn.run,
exiting non-zero (sys.exit(1)) and logging the DatabaseError
(host/port/database only, never the raw URL) at ERROR when the database
is unreachable.

New unit test test_app_call_exits_nonzero_naming_host_when_database_unreachable
monkeypatches check_connectivity (no live database, no real host lookup)
and asserts uvicorn.run is never called and SystemExit(1) is raised. The
existing T-0006 acceptance test (test_check_connectivity_names_host_on_
unreachable_url) already covers the underlying host-naming behavior at
the db layer.

Declared a new f_app_to_db flow in design/hullbreach.strata for the
app->db.engine import this wiring introduces (SYS003), noted the wiring
in sprint-1.md's fail-fast startup section (AFFECT001/DOC002), and
updated docs/index.md's App paragraph to describe the fail-fast check
(AFFECT001). No stale WIRE001 waivers referenced T-0099.

### Changed
```
 design/hullbreach.strata         |  8 ++++++++
 docs/design/sprint-1.md          |  6 +++---
 frob-coverage.lock.json          |  2 +-
 src/hullbreach_server/app/app.py | 20 ++++++++++++++++++++
 tests/unit/test_app.py           | 36 ++++++++++++++++++++++++++++++++++++
 tickets/T-0099/done-report.md    | 39 +++++++++++++++++++++++++++++++++++++++
 tickets/T-0099/ticket.md         | 26 +++++++++++++++++++++++++-
 7 files changed, 132 insertions(+), 5 deletions(-)
```

### Evidence
- `tests/unit/test_app.py::test_app_call_exits_nonzero_naming_host_when_database_unreachable` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 1 passed (from 1 evidence id(s))
- gates: unmeasured (no parsable gate-summary from a fresh check)
