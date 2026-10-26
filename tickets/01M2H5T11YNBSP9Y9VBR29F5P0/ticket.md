+++
id = "01M2H5T11YNBSP9Y9VBR29F5P0"
title = "GET /api/v1/leaderboard with the caller's own rank"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
points = 2
parent = "01M2H5T11XDV04575V7T3S9A68"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-26T08:49:05Z"
aliases = ["T-0062"]
labels = ["jira:SCRUM-190", "owner:lognd", "milestone:0.3.0", "creates:src/hullbreach_server/db/migrations/versions/d52f6a8b0c13_index_rating_changes_for_leaderboard.py"]
scope = ["src/hullbreach_server/api/leaderboard.py", "src/hullbreach_server/services/leaderboard.py", "tests/unit/test_leaderboard.py", "src/hullbreach_server/api/__init__.py", "src/hullbreach_server/auth/deps.py", "src/hullbreach_server/auth/__init__.py", "src/hullbreach_server/db/models/rating.py", "docs/index.md", "changelog.d/01M2H5T11YNBSP9Y9VBR29F5P0.added.md", "src/hullbreach_server/db/migrations/versions/d52f6a8b0c13_index_rating_changes_for_leaderboard.py"]

[[acceptance]]
text = "given a player ranked 340, when they fetch the top 100, then the response includes their rank 340"
bound = true
+++
