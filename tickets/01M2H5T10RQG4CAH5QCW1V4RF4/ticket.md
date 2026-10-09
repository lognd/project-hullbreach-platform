+++
id = "01M2H5T10RQG4CAH5QCW1V4RF4"
title = "Logout control in the site header"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
points = 1
parent = "01M2H5T10PSWBJQ94G2ER5HP1H"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:02Z"
aliases = ["T-0024"]
labels = ["jira:SCRUM-94", "owner:a-carten", "milestone:0.1.0"]
scope = ["web/src/components/Header.tsx", "web/tests/unit/Header.test.tsx", "web/src/api/auth.ts", "web/src/auth/session.ts", "docs/index.md", "design/hullbreach.strata"]

[[acceptance]]
text = "given a signed-in header, when logout is clicked, then the session is cleared and the landing page shows"
bound = false
+++
