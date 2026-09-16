---
id: T-draft-6eb03ea9
title: Add Alembic migration for the items table
state: queued
kind: feature
origin: human
created: '2026-09-16'
priority: medium
parent: null
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/db/migrations/versions/**
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
found while working T-0008: design section 4 / decision D3 say T-0007's migration set should include a minimal migration-owned items table (id UUID pk, slug String(64) unique, name String(120), price_cents Integer), but no such migration landed with T-0007. db/seed.py works around this by creating the table itself at runtime (Table.create(checkfirst=True)) so seed() and its tests do not depend on a live migration, but production Postgres should get this table from a real migration, not a lazy runtime create. Add the migration; seed.py's checkfirst=True create becomes a no-op once it exists.