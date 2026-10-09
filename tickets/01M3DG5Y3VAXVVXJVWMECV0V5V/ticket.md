+++
id = "01M3DG5Y3VAXVVXJVWMECV0V5V"
title = "S03-1: Unauthenticated GET /api/v1/health returning the running version"
type = "task"
category = "done"
outcome = "done"
priority = "high"
points = 1
parent = "01M2H5T10BYCP87BPHK38Y09BN"
reporter = "human"
created = "2026-09-26T00:00:00Z"
updated = "2026-10-09T04:06:45Z"
aliases = ["T-0123"]
labels = ["platform", "jira:SCRUM-83", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/api/health.py", "tests/unit/test_api.py"]

[[acceptance]]
text = "Given no credentials, when GET /api/v1/health is called, then it returns 200 with status ok and the running version"
bound = true
+++

https://aliens-against-humanity.atlassian.net/browse/SCRUM-83

Unauthenticated GET /api/v1/health returning the running version
Parent story: SCRUM-24
