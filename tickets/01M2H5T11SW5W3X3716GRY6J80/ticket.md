+++
id = "01M2H5T11SW5W3X3716GRY6J80"
title = "RatingChange rows written on match record and exposed with the match"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
points = 2
parent = "01M2H5T11QP42D39KC9ZNW0G2J"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-26T03:54:14Z"
aliases = ["T-0057"]
labels = ["jira:SCRUM-141", "owner:lognd", "milestone:0.2.0", "creates:src/hullbreach_server/db/migrations/versions/c41e5f7a9b02_create_rating_changes_table.py"]
scope = ["src/hullbreach_server/db/models/rating.py", "src/hullbreach_server/services/matches.py", "tests/unit/test_rating_history.py", "src/hullbreach_server/db/models/__init__.py", "docs/index.md", "src/hullbreach_server/db/migrations/versions/c41e5f7a9b02_create_rating_changes_table.py"]

[[acceptance]]
text = "given a recorded match, when fetched, then before and after ratings for both players are present"
bound = true
+++
