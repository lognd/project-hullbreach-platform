+++
id = "01M2H5T10BYCP87BPHK38Y09BN"
title = "S03 Confirm the API is alive"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T104B4HY0X1B5KX80SJ7"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0011"]
labels = ["jira:SCRUM-24", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/api/health.py", "tests/unit/test_api.py"]

[[acceptance]]
text = "given no credentials, when GET /api/v1/health is called, then 200 with the running version"
bound = false

[[acceptance]]
text = "given a local machine, when the endpoint is called, then it answers in under 100 ms"
bound = false
+++

As a game server, I want an unauthenticated endpoint that reports the API is up and which version it is, so that I can refuse to start a match when the platform is unreachable instead of losing results later.

Open questions:
- Should health also report database connectivity, or stay a pure liveness probe with a separate readiness endpoint?
