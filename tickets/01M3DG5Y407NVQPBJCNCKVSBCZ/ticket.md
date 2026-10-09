+++
id = "01M3DG5Y407NVQPBJCNCKVSBCZ"
title = "S15-2: Keyboard-only navigation pass on the header and footer"
type = "task"
category = "in-progress"
priority = "high"
points = 1
parent = "01M2H5T11BBT0FQHR5JDXDKE4Q"
reporter = "human"
created = "2026-09-26T00:00:00Z"
updated = "2026-10-09T03:58:48Z"
aliases = ["T-0128"]
labels = ["platform", "web", "jira:SCRUM-98", "owner:a-carten", "milestone:0.1.0"]
scope = ["web/src/App.tsx", "web/src/components/Footer.tsx", "web/src/components/Header.tsx", "web/src/router.tsx", "web/tests/unit/Header.test.tsx"]

[[acceptance]]
text = "Given the keyboard alone, when tabbing through the header and footer, then every link and control is reachable in visual order and Enter activates it"
bound = false
+++

https://aliens-against-humanity.atlassian.net/browse/SCRUM-98

Keyboard-only navigation pass on the header and footer
Parent story: SCRUM-36
