+++
id = "01M2H5T118CH0Q2PCGG2YF3KQN"
title = "PUT /api/v1/me/active-skin validating ownership, exposed in the session endpoint for the game"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T117A35Q8AA9THRZTTYB"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-09T16:38:09Z"
aliases = ["T-0040"]
labels = ["needs-game", "jira:SCRUM-187", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/me.py", "src/hullbreach_server/db/models/inventory.py", "tests/unit/test_active_skin.py"]

[[acceptance]]
text = "given an unowned item id, when set active, then 403 and the previous skin stays"
bound = false
+++
