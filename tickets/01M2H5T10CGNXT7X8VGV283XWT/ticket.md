+++
id = "01M2H5T10CGNXT7X8VGV283XWT"
title = "Readiness endpoint reporting database connectivity alongside the liveness health route"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
points = 2
parent = "01M2H5T10BYCP87BPHK38Y09BN"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:02Z"
aliases = ["T-0012"]
labels = ["jira:SCRUM-84", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/api/health.py", "tests/unit/test_api.py", "src/hullbreach_server/db/__init__.py", "docs/index.md", "design/hullbreach.strata", "src/hullbreach_server/db/engine.py"]

[[acceptance]]
text = "given a reachable database, when GET /api/v1/ready is called, then 200; when unreachable, then 503"
bound = false
+++
