+++
id = "01M2H5T12K6TESH4JBCVBT4P6C"
title = "Admin item CRUD endpoints with retire semantics"
type = "task"
category = "todo"
priority = "medium"
points = 3
parent = "01M2H5T12J047CP3Z2AC59XD4G"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0083"]
labels = ["jira:SCRUM-197", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/admin/items.py", "src/hullbreach_server/services/catalog.py", "tests/unit/test_admin_items.py"]

[[acceptance]]
text = "given a retired item, when the public catalog is fetched, then it is absent; when an owner's inventory is fetched, then present"
bound = false
+++
