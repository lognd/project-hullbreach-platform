+++
id = "01M5W0FEFC9SAFH2QQREV8F33K"
title = "Match payouts violate the ledger FK on PostgreSQL (make demo fails)"
type = "bug"
category = "todo"
priority = "high"
reporter = "a-carten"
created = "2026-10-26T11:45:34Z"
updated = "2026-10-26T11:50:21Z"
labels = ["owner:a-carten", "creates:changelog.d/01M5W0FEFC9SAFH2QQREV8F33K.fixed.md", "creates:tests/system/test_phone_width.py", "creates:tests/system/phone_width.mjs", "creates:changelog.d/01M2H5T10YFV60H1CQDEEH5164.added.md"]
scope = ["src/hullbreach_server/services/matches.py", "tests/unit/test_currency.py", "changelog.d/01M5W0FEFC9SAFH2QQREV8F33K.fixed.md", "docs/index.md", "tests/system/test_phone_width.py", "tests/system/phone_width.mjs", "changelog.d/01M2H5T10YFV60H1CQDEEH5164.added.md"]
+++

Found in real-browser store QA: record_match staged currency_ledger rows with no relationship() to the match, so PostgreSQL got the ledger INSERT before the matches INSERT (fk_currency_ledger_match_id_matches). make demo died seeding demo accounts; POST /matches would 500 on Postgres. SQLite tests do not enforce FKs. Fix: flush the match before staging payouts.
