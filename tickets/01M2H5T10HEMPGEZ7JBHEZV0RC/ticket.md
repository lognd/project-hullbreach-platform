+++
id = "01M2H5T10HEMPGEZ7JBHEZV0RC"
title = "Website register page with inline validation errors"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
points = 3
parent = "01M2H5T10EF0AKZ2JZC55N747C"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:02Z"
aliases = ["T-0017"]
labels = ["jira:SCRUM-88", "owner:a-carten", "milestone:0.1.0"]
scope = ["web/src/pages/Register.tsx", "web/src/api/auth.ts", "web/tests/unit/Register.test.tsx", "web/src/router.tsx", "docs/index.md", "design/hullbreach.strata", "docs/design/registry/capability-via-ratchet.lock.json"]

[[acceptance]]
text = "given the register form, when the API returns a field error, then it is shown next to the field"
bound = false
+++
