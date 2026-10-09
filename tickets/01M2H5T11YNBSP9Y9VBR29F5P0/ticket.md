+++
id = "01M2H5T11YNBSP9Y9VBR29F5P0"
title = "GET /api/v1/leaderboard with the caller's own rank"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T11XDV04575V7T3S9A68"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0062"]
labels = ["jira:SCRUM-190", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/leaderboard.py", "src/hullbreach_server/services/leaderboard.py", "tests/unit/test_leaderboard.py"]

[[acceptance]]
text = "given a player ranked 340, when they fetch the top 100, then the response includes their rank 340"
bound = false
+++
