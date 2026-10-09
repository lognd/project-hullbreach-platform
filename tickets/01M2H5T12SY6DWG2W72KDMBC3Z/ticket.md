+++
id = "01M2H5T12SY6DWG2W72KDMBC3Z"
title = "ShipDesign model and CRUD under /api/v1/me/designs storing the design as validated JSON"
type = "task"
category = "todo"
priority = "medium"
points = 3
parent = "01M2H5T12R5AJV3F3ZWEPGM24D"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0089"]
labels = ["needs-game", "jira:SCRUM-175", "owner:lognd", "milestone:0.2.0"]
scope = ["src/hullbreach_server/db/models/design.py", "src/hullbreach_server/api/designs.py", "tests/unit/test_designs.py"]

[[acceptance]]
text = "given a design over the size limit, when saved, then 413 with the limit named"
bound = false
+++
