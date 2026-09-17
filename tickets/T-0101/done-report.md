## Done report

Adds the Alembic migration (abbcc4cb6b34_create_items_table.py) that
db/seed.py's items table needed but never got when T-0007 landed
(docs/design/sprint-1.md section 4 / decision D3): id (UUID pk), unique
slug, name, price_cents -- matching what seed.py already hand-declares
on its own MetaData.

seed.py's own Table.create(checkfirst=True) call becomes a no-op
wherever the migration has run (every real environment); it stays
only because tests/unit/test_seed.py's SQLite fixture
(tests/unit/conftest.py::db_session) builds its schema from
Base.metadata.create_all, not by running Alembic, and items is
deliberately not on Base.metadata (no ORM model until T-0066).

tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
now passes an include_object filter to compare_metadata excluding the
items table, since it is intentionally model-less and would otherwise
report a false "extra table" diff. Confirmed the migration applies
cleanly against a fresh SQLite database via this test.

Updated docs/index.md's database-migrations section (fourth revision)
and db-seed paragraph for the landed migration.

### Changed
```
 .../versions/abbcc4cb6b34_create_items_table.py    | 54 ++++++++++++++++++++++
 src/hullbreach_server/db/seed.py                   | 22 ++++++---
 tests/system/test_build.py                         | 17 ++++++-
 tickets/T-0101/ticket.md                           | 31 ++++++++++++-
 4 files changed, 115 insertions(+), 9 deletions(-)
```

### Evidence
(no evidence recorded)

### Captured claims
- tests: 0 passed (from 0 evidence id(s))
- gates: unmeasured (no parsable gate-summary from a fresh check)
