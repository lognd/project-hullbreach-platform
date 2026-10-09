+++
id = "01M2H5T110VJQSF0684JXFR6E8"
title = "Website profile page, responsive to phone width"
type = "task"
category = "in-progress"
priority = "medium"
points = 3
parent = "01M2H5T10YFV60H1CQDEEH5164"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-09T04:01:04Z"
aliases = ["T-0032"]
labels = ["jira:SCRUM-146", "owner:a-carten", "milestone:0.2.0"]
scope = ["web/src/pages/Profile.tsx", "web/tests/unit/Profile.test.tsx", "web/src/api/me.ts", "web/src/api/auth.ts", "web/src/router.tsx", "web/src/components/MatchItem.tsx", "web/tests/fixtures/me.ts", "web/tests/support/layout.ts"]

[[acceptance]]
text = "given the profile page at 400px, when rendered, then nothing overflows horizontally"
bound = false

[[acceptance]]
text = "Given a signed-in player and a GET /api/v1/me response, when the profile page loads, then username, rating, currency, owned skins and the last five matches show"
bound = false

[[acceptance]]
text = "Given a signed-out visitor, when the profile page renders, then it asks them to log in and makes no request"
bound = false
+++
