+++
id = "01M3DG5Y3STPYB6G3GGXJE6766"
title = "S02-1: GitHub Actions workflow running lint, type checks, and tests for both the Python and TypeScript halves"
type = "task"
category = "todo"
priority = "critical"
points = 3
parent = "01M2H5T109596X8JSBWC05JJDV"
reporter = "human"
created = "2026-09-26T00:00:00Z"
updated = "2026-10-09T04:06:24Z"
aliases = ["T-0121"]
labels = ["infra", "platform", "jira:SCRUM-79", "owner:lognd", "milestone:0.1.0"]
scope = ["CONTRIBUTING.md", "README.md"]

[[acceptance]]
text = "Given a pull request to main, when CI runs, then the server job runs ruff check, ruff format --check, ty check and pytest"
bound = true

[[acceptance]]
text = "Given a pull request to main, when CI runs, then the web job runs eslint, prettier, crunk, tsc, vitest and the vite build"
bound = true
+++

https://aliens-against-humanity.atlassian.net/browse/SCRUM-79

GitHub Actions workflow running lint, type checks, and tests for both the Python and TypeScript halves
Parent story: SCRUM-23
