+++
id = "01M2H5T12QQ1GTD3DJW1KEGC1Y"
title = "Queue endpoints: join, status, cancel, with rating-window pairing and server assignment"
type = "task"
category = "todo"
priority = "medium"
points = 5
parent = "01M2H5T12PWAJEVZ18CDFJCG57"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0087"]
labels = ["needs-game", "jira:SCRUM-168", "owner:lognd", "milestone:0.2.0"]
scope = ["src/hullbreach_server/api/matchmaking.py", "src/hullbreach_server/services/matchmaking.py", "tests/unit/test_matchmaking.py"]

[[acceptance]]
text = "given two players within 100 rating, when both are queued, then status returns the same match id and server address for both"
bound = false
+++
