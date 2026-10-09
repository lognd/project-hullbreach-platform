+++
id = "01M2H5T11PZ6JDPS66PNFRX5S2"
title = "POST /api/v1/matches with an idempotency key, recording result and stats"
type = "task"
category = "todo"
priority = "medium"
points = 3
parent = "01M2H5T11KNPF6MRRJKJR6793R"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0054"]
labels = ["needs-game", "jira:SCRUM-138", "owner:lognd", "milestone:0.2.0"]
scope = ["src/hullbreach_server/api/matches.py", "src/hullbreach_server/services/matches.py", "tests/unit/test_matches_record.py"]

[[acceptance]]
text = "given the same idempotency key twice, when posted, then one match exists and both responses agree"
bound = false
+++
