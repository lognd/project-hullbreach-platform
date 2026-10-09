+++
id = "01M3DG5Y3RH2BNDS9FVAX3GZR4"
title = "S01-5: Document the local Docker PostgreSQL setup and the hosted database switch in the README"
type = "task"
category = "todo"
priority = "critical"
points = 1
parent = "01M2H5T105AGGPXTV9ETEC5DF2"
reporter = "human"
created = "2026-09-26T00:00:00Z"
updated = "2026-10-09T04:06:13Z"
aliases = ["T-0120"]
labels = ["infra", "platform", "jira:SCRUM-78", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/__main__.py", "src/hullbreach_server/db/__init__.py", "src/hullbreach_server/db/engine.py", "src/hullbreach_server/db/migrations/", "src/hullbreach_server/db/seed.py", "src/hullbreach_server/db/seed_items.json", "tests/system/test_build.py", "tests/unit/test_db_engine.py", "tests/unit/test_seed.py"]

[[acceptance]]
text = "Given a new developer reading the README, when they follow it, then they can start the local Docker PostgreSQL (docker compose up -d db) and find troubleshooting for it"
bound = true

[[acceptance]]
text = "Given a developer with a shared or hosted database, when they read the README, then they know switching is setting HULLBREACH_DATABASE_URL, with no code change"
bound = true
+++

https://aliens-against-humanity.atlassian.net/browse/SCRUM-78

Document the local Docker PostgreSQL setup and the hosted database switch in the README
Parent story: SCRUM-22
