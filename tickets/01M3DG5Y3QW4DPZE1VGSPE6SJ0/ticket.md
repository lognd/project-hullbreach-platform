+++
id = "01M3DG5Y3QW4DPZE1VGSPE6SJ0"
title = "S01-4: Unit tests for the engine dependency and the seed command"
type = "task"
category = "todo"
priority = "critical"
points = 2
parent = "01M2H5T105AGGPXTV9ETEC5DF2"
reporter = "human"
created = "2026-09-26T00:00:00Z"
updated = "2026-10-09T04:05:48Z"
aliases = ["T-0119"]
labels = ["infra", "platform", "jira:SCRUM-77", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/__main__.py", "src/hullbreach_server/db/__init__.py", "src/hullbreach_server/db/engine.py", "src/hullbreach_server/db/migrations/", "src/hullbreach_server/db/seed.py", "src/hullbreach_server/db/seed_items.json", "tests/system/test_build.py", "tests/unit/test_db_engine.py", "tests/unit/test_seed.py"]

[[acceptance]]
text = "Given an unreachable or reachable database URL, when connectivity is checked, then the result names the host but never the password, and a reachable engine returns Ok; the get_db dependency yields a session"
bound = true

[[acceptance]]
text = "Given an initialized database, when the seed runs twice, then 100 catalog items and one admin exist, the second run duplicates nothing, and a missing admin password is an Err"
bound = false
+++

https://aliens-against-humanity.atlassian.net/browse/SCRUM-77

Unit tests for the engine dependency and the seed command
Parent story: SCRUM-22
