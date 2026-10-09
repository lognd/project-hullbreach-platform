+++
id = "01M2H5T10N473QS7WDAWZH7HB5"
title = "Website login page and persisted session across reloads"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
points = 3
parent = "01M2H5T10JTJB218KF4C7FSH46"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:02Z"
aliases = ["T-0021"]
labels = ["jira:SCRUM-92", "owner:a-carten", "milestone:0.1.0"]
scope = ["web/src/pages/Login.tsx", "web/src/auth/session.ts", "web/tests/unit/Login.test.tsx", "web/src/router.tsx", "docs/index.md", "web/src/api/auth.ts", "design/hullbreach.strata"]

[[acceptance]]
text = "given a login, when the page reloads, then the user is still shown as signed in"
bound = false
+++
