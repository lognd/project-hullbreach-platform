+++
id = "01M2H5T123XSEESJJVAE8NS2PN"
title = "GET /api/v1/catalog with category filter and owned flag for the caller"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T121VAJY5NDGSEH8PTH7"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0067"]
labels = ["jira:SCRUM-182", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/catalog.py", "src/hullbreach_server/services/catalog.py", "tests/unit/test_catalog.py"]

[[acceptance]]
text = "given an owned item, when the catalog is fetched signed in, then owned is true for it only"
bound = false
+++
