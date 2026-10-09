+++
id = "01M2H5T11SW5W3X3716GRY6J80"
title = "RatingChange rows written on match record and exposed with the match"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T11QP42D39KC9ZNW0G2J"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0057"]
labels = ["jira:SCRUM-141", "owner:lognd", "milestone:0.2.0"]
scope = ["src/hullbreach_server/db/models/rating.py", "src/hullbreach_server/services/matches.py", "tests/unit/test_rating_history.py"]

[[acceptance]]
text = "given a recorded match, when fetched, then before and after ratings for both players are present"
bound = false
+++
