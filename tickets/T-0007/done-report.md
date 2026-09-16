## Done report

Changed (this round, on top of the prior Done report):
- Deleted src/hullbreach_server/db/migrations/README (REF001: Alembic's
  scaffold README had no inbound reference; docs/index.md is the doc home)
- frob.toml: [[refs.entrypoint]] for script.py.mako (REF002: read by
  Alembic's `revision` command by convention via alembic.ini's
  script_location, not referenced by name from tracked source)
- docs/index.md: new "### Database migrations" subsection (anchor
  #database-migrations) describing db upgrade/db seed, env.py's two
  entrypoints, script.py.mako, and the baseline revision; reworded the
  "not implemented yet" phrasing to a positive statement (db seed
  "builds on ... that lands in T-0008", <!-- frob:until T-0008 -->) and
  to "always refuses... only online migrations are supported for 0.1.0"
  (NEGEXIST001)
- env.py: `# frob:doc docs/index.md#database-migrations` above both
  run_migrations_offline and run_migrations_online (COV001); dropped the
  now-redundant LANDPARITY001 waiver on run_migrations_offline since the
  doc directive satisfies it directly

Rebase: onto origin/main (PR #7, #12 merged) picked up T-0003's close,
so CROSSTICKET001 on tickets/T-0007/ticket.md is gone, and App.tsx's
COV001 was already resolved upstream -- neither needed touching here.

Evidence: unchanged from before (tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata,
bound to acceptance [1]).

Gates: `frob check --base origin/main --ticket T-0007` -- 0 errors, 81
warnings, 1 unresolved (gate:FLAGCOV, pre-existing/unrelated), 48 waived.
Exact CI sequence run locally: ruff check/format, ty check, `uv run
pytest tests/ -n auto -q` (all green); `npx tsc --noEmit`, `npx eslint .`,
`npx vitest run` (36/36, all green, after `npm ci` picked up
@testing-library/user-event from a sibling ticket's package.json change).

### Changed
```
 alembic.ini                                        | 152 +++++++++++++++++++++
 design/hullbreach.strata                           |   8 +-
 docs/index.md                                      |  15 +-
 frob-coverage.lock.json                            |   4 +-
 pyproject.toml                                     |   1 +
 src/hullbreach_server/__main__.py                  |  30 ++++
 src/hullbreach_server/db/migrations/README         |   1 +
 src/hullbreach_server/db/migrations/env.py         |  72 ++++++++++
 src/hullbreach_server/db/migrations/script.py.mako |  28 ++++
 .../ba2efc248a9a_baseline_no_tables_yet.py         |  35 +++++
 tests/system/test_build.py                         |  24 ++--
 tickets/T-0007/done-report.md                      |  60 ++++++++
 tickets/T-0007/ticket.md                           |  52 ++++++-
 uv.lock                                            | 102 ++++++++++++++
 14 files changed, 561 insertions(+), 23 deletions(-)
```

### Evidence
- `tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 1 passed (from 1 evidence id(s))
- gates: unmeasured (no parsable gate-summary from a fresh check)
