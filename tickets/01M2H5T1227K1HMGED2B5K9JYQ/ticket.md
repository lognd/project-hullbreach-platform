+++
id = "01M2H5T1227K1HMGED2B5K9JYQ"
title = "Item and Inventory models with categories and migration"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T121VAJY5NDGSEH8PTH7"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-09T16:38:09Z"
aliases = ["T-0066"]
labels = ["jira:SCRUM-181", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/db/models/item.py", "src/hullbreach_server/db/models/inventory.py", "src/hullbreach_server/db/migrations/", "tests/unit/test_item_models.py"]

[[acceptance]]
text = "given the seed, when items are loaded, then every item has a category from the enum"
bound = false
+++
