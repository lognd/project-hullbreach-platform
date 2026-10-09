+++
id = "01M2H5T11594WX75ZK5S9FQ3HQ"
title = "DELETE /api/v1/me anonymizing the user and revoking sessions while keeping match rows"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T114G1C2NS9KF4WKN7VA"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0037"]
labels = ["jira:SCRUM-149", "owner:lognd", "milestone:0.2.0"]
scope = ["src/hullbreach_server/api/me.py", "src/hullbreach_server/services/account_deletion.py", "tests/unit/test_me_delete.py"]

[[acceptance]]
text = "given a deleted user, when an opponent's match list is fetched, then the opponent name is a placeholder"
bound = false
+++
