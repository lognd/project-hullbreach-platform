+++
id = "01M2H5T108QJ1XZE5WZKK7Y5KS"
title = "Seed command loading 100+ catalog items and the first admin account"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
points = 3
parent = "01M2H5T105AGGPXTV9ETEC5DF2"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:02Z"
aliases = ["T-0008"]
labels = ["jira:SCRUM-76", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/db/seed.py", "src/hullbreach_server/db/seed_items.json", "tests/unit/test_seed.py", "src/hullbreach_server/__main__.py", "src/hullbreach_server/auth/passwords.py", "docs/index.md", "design/hullbreach.strata", "docs/design/sprint-1.md", ".env.example", "docs/design/registry/capability-via-ratchet.lock.json"]

[[acceptance]]
text = "given an empty database, when seed runs, then item count >= 100 and one Administrator exists"
bound = false

[[acceptance]]
text = "given a seeded database, when seed runs again, then nothing is duplicated"
bound = false
+++
