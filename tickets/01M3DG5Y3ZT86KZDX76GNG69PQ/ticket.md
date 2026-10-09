+++
id = "01M3DG5Y3ZT86KZDX76GNG69PQ"
title = "S17-3: Elo unit tests (winner never loses, loser never gains)"
type = "task"
category = "todo"
priority = "high"
points = 1
parent = "01M2H5T11QP42D39KC9ZNW0G2J"
reporter = "human"
created = "2026-09-26T00:00:00Z"
updated = "2026-10-09T04:00:33Z"
aliases = ["T-0127"]
labels = ["platform", "jira:SCRUM-142", "owner:lognd", "milestone:0.2.0"]
scope = ["docs/index.md", "tests/unit/test_elo.py"]

[[acceptance]]
text = "Given any two ratings at or above the floor, when the winner's and loser's new ratings are computed, then the winner's rating is never lower than before"
bound = false

[[acceptance]]
text = "Given any two ratings at or above the floor, when the winner's and loser's new ratings are computed, then the loser's rating is never higher than before"
bound = false
+++

https://aliens-against-humanity.atlassian.net/browse/SCRUM-142

Elo unit tests (winner never loses, loser never gains)
Parent story: SCRUM-38
