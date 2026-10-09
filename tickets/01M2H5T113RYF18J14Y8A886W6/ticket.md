+++
id = "01M2H5T113RYF18J14Y8A886W6"
title = "Website account settings form"
type = "task"
category = "in-progress"
priority = "medium"
points = 2
parent = "01M2H5T11109WWPFDDD0ZX7K9V"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-09T04:09:05Z"
aliases = ["T-0035"]
labels = ["jira:SCRUM-148", "owner:a-carten", "milestone:0.2.0"]
scope = ["web/src/pages/Settings.tsx", "web/tests/unit/Settings.test.tsx", "web/src/api/me.ts", "web/tests/fixtures/me.ts", "web/src/router.tsx", "web/src/components/SignInPrompt.tsx", "web/src/pages/Profile.tsx", "docs/index.md"]

[[acceptance]]
text = "given a wrong current password, when saving, then the error is shown and nothing changes"
bound = true

[[acceptance]]
text = "Given the current password, when the email or password is changed, then PATCH /api/v1/me is sent with only the changed fields and success is shown"
bound = true

[[acceptance]]
text = "Given an email or password change without the current password, when saving, then an inline error is shown and no request is sent"
bound = true

[[acceptance]]
text = "Given a display name the server rejects (409 or 422), when saving, then the server's message shows next to that field"
bound = true
+++
