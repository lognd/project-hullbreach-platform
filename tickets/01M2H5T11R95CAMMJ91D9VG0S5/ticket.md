+++
id = "01M2H5T11R95CAMMJ91D9VG0S5"
title = "Pure Elo module with documented K-factor, starting rating, and floor"
type = "task"
category = "in-progress"
priority = "medium"
points = 2
parent = "01M2H5T11QP42D39KC9ZNW0G2J"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-09T03:59:02Z"
aliases = ["T-0056"]
labels = ["jira:SCRUM-140", "owner:lognd", "milestone:0.2.0", "creates:src/hullbreach_server/rating/__init__.py"]
scope = ["src/hullbreach_server/rating/elo.py", "docs/index.md", "tests/unit/test_elo.py", "src/hullbreach_server/rating/__init__.py"]

[[acceptance]]
text = "given equal ratings, when the higher-rated loses, then the change magnitude is larger than an expected win"
bound = false

[[acceptance]]
text = "Given the module is read, when a caller needs the K-factor, starting rating, floor or rounding rule, then each is a named constant or documented behavior in rating/elo.py and described in docs/index.md"
bound = false

[[acceptance]]
text = "Given a loser whose rating is at or near the floor, when ratings update, then the loser's new rating is never below the floor"
bound = false
+++
