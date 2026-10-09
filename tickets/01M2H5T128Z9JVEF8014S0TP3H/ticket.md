+++
id = "01M2H5T128Z9JVEF8014S0TP3H"
title = "POST /api/v1/store/purchase as a single transaction with a uniqueness constraint on (user, item)"
type = "task"
category = "todo"
priority = "medium"
points = 3
parent = "01M2H5T127FEKMSVQSA2K2YHED"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0072"]
labels = ["jira:SCRUM-185", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/store.py", "src/hullbreach_server/services/store.py", "tests/unit/test_store_purchase.py"]

[[acceptance]]
text = "given two concurrent purchases of one item, when both run, then one succeeds and one is refused with no double debit"
bound = false
+++
