+++
id = "01M2KR6R359Z2X63K2113CTW2Y"
title = "Add Alembic migration for the items table"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
reporter = "human"
created = "2026-09-16T00:00:00Z"
updated = "2026-09-16T00:00:02Z"
aliases = ["T-0101"]
labels = ["jira:none"]
scope = ["src/hullbreach_server/db/migrations/versions/**", "src/hullbreach_server/db/seed.py", "tests/unit/test_seed.py", "tests/system/test_build.py", "docs/index.md"]
+++

found while working T-0008: design section 4 / decision D3 say T-0007's migration set should include a minimal migration-owned items table (id UUID pk, slug String(64) unique, name String(120), price_cents Integer), but no such migration landed with T-0007. db/seed.py works around this by creating the table itself at runtime (Table.create(checkfirst=True)) so seed() and its tests do not depend on a live migration, but production Postgres should get this table from a real migration, not a lazy runtime create. Add the migration; seed.py's checkfirst=True create becomes a no-op once it exists.
