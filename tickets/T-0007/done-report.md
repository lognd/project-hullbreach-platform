## Done report

Changed:
- alembic.ini (repo root; script_location = src/hullbreach_server/db/migrations)
- src/hullbreach_server/db/migrations/env.py (run_migrations_online/offline)
- src/hullbreach_server/db/migrations/script.py.mako (standard Alembic template)
- src/hullbreach_server/db/migrations/versions/ba2efc248a9a_baseline_no_tables_yet.py::upgrade
- src/hullbreach_server/db/migrations/versions/ba2efc248a9a_baseline_no_tables_yet.py::downgrade
- src/hullbreach_server/__main__.py (db subparser group: upgrade wired to
  alembic.config.main; seed is a stub pointing at T-0008, no import of the
  not-yet-existing db/seed.py so ty check stays clean)
- docs/index.md (CLI section synced), pyproject.toml/uv.lock (alembic dep)

Design decision: the first migration is a no-op baseline. Section 2 (data
model) attributes User to T-0015 and Session to T-0019 only; T-0007 owns
no table. Section 4's items-table/D3 discussion is scoped to T-0008's
seeding problem and explicitly says that Table is hand-declared in
seed.py (T-0008, does not exist yet) -- landing it here would desync
Base.metadata (empty) from the migrated schema and fail the acceptance
test's compare_metadata check. An empty baseline keeps both empty and
in sync; T-0015/T-0019 add the first real migrations.

Evidence: tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
(bound to acceptance [1]) -- builds a throwaway SQLite engine, runs
`alembic upgrade head` against it, and asserts compare_metadata reports
no diffs against Base.metadata. xfail marker removed. Full suite green
locally (`uv run pytest tests/ -n auto -q`) and via `uv run ty check src/`,
`uv run ruff check/format`, `python -m typani.lint src`.

Filed: none. T-0099 (wire check_connectivity into App.__call__) is NOT
folded into this ticket: design section 4 says `db upgrade`/`db seed`
"exit without starting uvicorn" and "neither subcommand builds
App/create_app" -- the fail-fast wiring (App.__call__ before uvicorn.run,
decision D2, section 3) is a disjoint code path in app/app.py that this
ticket's scope never touches. T-0099 stays queued for whoever picks up
app/app.py.

Gates: frob check --base origin/main --ticket T-0007 clean except the
same structural CROSSTICKET001 on tickets/T-0007/ticket.md (T-0003's
'tickets/**' lease, still in-progress) seen and confirmed non-blocking
in T-0006's real CI run (PR #10 passed with only gate:SCOPE findings,
no CROSSTICKET row at all -- that gate appears to depend on local
cross-worktree lease state absent from a fresh CI checkout).
Waivers: WIRE001 on migrations/versions/...::upgrade and ::downgrade
(reflective/Alembic-only invocation, follow_up T-0015); TEST001 on
::downgrade (no-op revert path). ruff check/format, ty check, and
typani.lint all pass. `uv run pytest tests/ -n auto -q`: all green.

### Changed
```
 tickets/T-0007/ticket.md | 35 ++++++++++++++++++++++++++++++++++-
 1 file changed, 34 insertions(+), 1 deletion(-)
```

### Evidence
- `tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 1 passed (from 1 evidence id(s))
- gates: unmeasured (no parsable gate-summary from a fresh check)
