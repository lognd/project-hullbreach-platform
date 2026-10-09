+++
id = "01M2H5T12DHERRG7PFSX31A3MK"
title = "Suspension state with ModerationLog rows; login refuses suspended players with the reason"
type = "task"
category = "todo"
priority = "medium"
points = 3
parent = "01M2H5T12BT56ETFWBMD8MR8HR"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0077"]
labels = ["jira:SCRUM-193", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/db/models/moderation.py", "src/hullbreach_server/api/admin/players.py", "src/hullbreach_server/api/auth.py", "tests/unit/test_moderation.py"]

[[acceptance]]
text = "given a suspended player, when they log in, then 403 carrying the suspension reason"
bound = false
+++
