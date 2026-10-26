+++
id = "01M2H5T11GEGRR23QSDXER9PXR"
title = "Cookie notice component with dismissal remembered in localStorage"
type = "task"
category = "todo"
priority = "medium"
points = 1
parent = "01M2H5T11FAFM60K6X25WQSF10"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-26T09:36:10Z"
aliases = ["T-0048"]
labels = ["jira:SCRUM-209", "owner:a-carten", "milestone:0.3.0"]
scope = ["web/src/components/CookieNotice.tsx", "web/tests/unit/CookieNotice.test.tsx", "web/src/App.tsx", "web/tests/unit/App.test.tsx", "web/src/**", "web/tests/unit/**", "changelog.d/*.added.md", "docs/index.md", "changelog.d/01M2H5T11GEGRR23QSDXER9PXR.added.md", "changelog.d/01M2H5T11HZP2VXR9KV24Q8RV3.added.md", "changelog.d/01M2H5T11EWXN4QEQ0QET8ZC6Y.added.md"]

[[acceptance]]
text = "given a dismissed notice, when the page reloads, then it does not show"
bound = true
+++
