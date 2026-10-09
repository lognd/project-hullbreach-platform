+++
id = "01M2H5T11MXDGNF6DR3TT12YE3"
title = "Game-server API key authentication dependency"
type = "task"
category = "in-progress"
priority = "medium"
points = 2
parent = "01M2H5T11KNPF6MRRJKJR6793R"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-09T04:02:55Z"
aliases = ["T-0052"]
labels = ["needs-game", "jira:SCRUM-136", "owner:lognd", "milestone:0.2.0"]
scope = ["src/hullbreach_server/auth/server_keys.py", "src/hullbreach_server/app/config.py", "tests/unit/test_server_keys.py", "docs/index.md"]

[[acceptance]]
text = "given a missing or wrong key, when the match endpoint is called, then 401"
bound = true

[[acceptance]]
text = "Given a request carrying a configured server key, when the match endpoint is called, then the request is authenticated"
bound = true

[[acceptance]]
text = "Given no server keys are configured, when any key is presented, then the request is rejected with 401"
bound = true
+++
