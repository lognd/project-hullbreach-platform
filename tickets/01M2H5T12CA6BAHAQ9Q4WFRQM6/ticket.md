+++
id = "01M2H5T12CA6BAHAQ9Q4WFRQM6"
title = "Admin player search and detail endpoints under /api/v1/admin"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T12BT56ETFWBMD8MR8HR"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0076"]
labels = ["jira:SCRUM-192", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/admin/players.py", "src/hullbreach_server/services/admin.py", "tests/unit/test_admin_players.py"]

[[acceptance]]
text = "given a partial username, when searched by an admin, then matching players return; a Player gets 403"
bound = false
+++
