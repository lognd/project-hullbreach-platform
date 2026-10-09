+++
id = "01M2H5T109596X8JSBWC05JJDV"
title = "S02 Block merges that fail the quality gate"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T104B4HY0X1B5KX80SJ7"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0009"]
labels = ["jira:SCRUM-23", "owner:lognd", "milestone:0.1.0"]
scope = ["CONTRIBUTING.md", "README.md"]

[[acceptance]]
text = "given a pull request with a failing check, when a non-bypass member tries to merge, then GitHub refuses"
bound = false

[[acceptance]]
text = "given the required check, when it runs, then it covers both the Python and TypeScript halves"
bound = false

[[acceptance]]
text = "given the README, when a teammate runs the gate locally, then they get the same result as CI"
bound = false
+++

As a developer, I want every pull request to run lint, type checks, tests, and the design-system check before it can merge into main, so that a broken change never reaches the branch we demo from.

Open questions:
- Is frob a required status check from day one, or advisory while the team learns it?
- One approving review required, or is green CI enough for small changes?
