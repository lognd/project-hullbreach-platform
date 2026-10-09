+++
id = "01M4GR0YEFS0660XADJ4DFR7AP"
title = "seed(): _upsert_items is insert-if-missing; docstring/log claim upsert, catalog edits never propagate"
type = "bug"
category = "todo"
priority = "low"
reporter = "lognd"
created = "2026-10-09T16:30:30Z"
updated = "2026-10-09T16:30:30Z"
labels = ["origin:auditor", "audit:db"]
scope = ["src/hullbreach_server/db/seed.py"]
+++

db/seed.py:93-112. on_conflict_do_nothing(index_elements=['slug']) (line 111) means a changed name or price in seed_items.json is silently ignored on re-seed, while the docstring and _log.info('seeded %d catalog item(s)') (seed.py:~131) claim all rows were seeded/upserted. Wrong-but-not-erroring result for a price change. Fix: use on_conflict_do_update(index_elements=['slug'], set_={name, price_cents}) (supported on both postgresql and sqlite dialects) or rename/doc as insert-only and log the inserted count from rowcount.
