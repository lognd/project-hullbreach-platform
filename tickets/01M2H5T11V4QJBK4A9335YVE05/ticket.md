+++
id = "01M2H5T11V4QJBK4A9335YVE05"
title = "GET /api/v1/me/matches with cursor pagination"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T11T3DJZ8N35J58RKTZ4"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0059"]
labels = ["jira:SCRUM-143", "owner:lognd", "milestone:0.2.0"]
scope = ["src/hullbreach_server/api/me.py", "src/hullbreach_server/services/matches.py", "tests/unit/test_me_matches.py"]

[[acceptance]]
text = "given 250 matches, when paging with the cursor, then every match appears exactly once, newest first"
bound = false
+++
