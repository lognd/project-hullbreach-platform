+++
id = "01M2H5T12VZC42N2PAWH0P8H5P"
title = "POST /api/v1/trust-events from the game server and listing on the admin player detail"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T12TXF5DD4SP3T4WFC8A"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0091"]
labels = ["needs-game", "jira:SCRUM-204", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/trust.py", "src/hullbreach_server/db/models/trust.py", "src/hullbreach_server/api/admin/players.py", "tests/unit/test_trust_events.py"]

[[acceptance]]
text = "given a posted trust event, when the admin detail is fetched, then it appears with time and kind"
bound = false
+++
