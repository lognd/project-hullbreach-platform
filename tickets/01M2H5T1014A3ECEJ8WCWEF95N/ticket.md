+++
id = "01M2H5T1014A3ECEJ8WCWEF95N"
title = "Scaffold the platform monorepo"
type = "task"
category = "done"
outcome = "done"
priority = "high"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:02Z"
aliases = ["T-0001"]
labels = ["jira:none"]
scope = ["src/**", "tests/**", "web/**", "docs/**", "*", ".github/**", "invariants/**", "tickets/**"]

[[acceptance]]
text = "given a fresh clone, when uv sync and npm ci run, then frob check reports 0 errors"
bound = false

[[acceptance]]
text = "given create_app, when GET /api/v1/health, then 200 with status ok"
bound = false
+++
