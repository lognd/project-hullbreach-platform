+++
id = "01M2H5T11R95CAMMJ91D9VG0S5"
title = "Pure Elo module with documented K-factor, starting rating, and floor"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T11QP42D39KC9ZNW0G2J"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0056"]
labels = ["jira:SCRUM-140", "owner:lognd", "milestone:0.2.0"]
scope = ["src/hullbreach_server/rating/elo.py", "docs/index.md", "tests/unit/test_elo.py"]

[[acceptance]]
text = "given equal ratings, when the higher-rated loses, then the change magnitude is larger than an expected win"
bound = false
+++
