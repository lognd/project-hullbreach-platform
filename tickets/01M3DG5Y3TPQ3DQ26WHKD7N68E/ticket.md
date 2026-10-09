+++
id = "01M3DG5Y3TPQ3DQ26WHKD7N68E"
title = "S02-2: Add the design-system (frob) check as a required CI step"
type = "task"
category = "todo"
priority = "critical"
points = 2
parent = "01M2H5T109596X8JSBWC05JJDV"
reporter = "human"
created = "2026-09-26T00:00:00Z"
updated = "2026-10-09T04:06:27Z"
aliases = ["T-0122"]
labels = ["infra", "platform", "jira:SCRUM-80", "owner:lognd", "milestone:0.1.0"]
scope = ["CONTRIBUTING.md", "README.md"]

[[acceptance]]
text = "Given a pull request to main, when CI runs, then a dedicated frob check job runs frob ticket doctor and frob check, and fails the PR on a finding at or above fail_on"
bound = true

[[acceptance]]
text = "Given a contributor reading CONTRIBUTING.md, when they look for what merges a PR, then frob check is named as one of the required status checks"
bound = true
+++

https://aliens-against-humanity.atlassian.net/browse/SCRUM-80

Add the design-system (frob) check as a required CI step
Parent story: SCRUM-23
