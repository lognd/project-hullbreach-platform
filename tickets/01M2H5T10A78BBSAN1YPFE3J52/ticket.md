+++
id = "01M2H5T10A78BBSAN1YPFE3J52"
title = "Require one approving review and All checks pass in branch protection; document it"
type = "docs"
category = "done"
outcome = "done"
priority = "medium"
points = 1
parent = "01M2H5T109596X8JSBWC05JJDV"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:03Z"
aliases = ["T-0010"]
labels = ["jira:SCRUM-81", "owner:lognd", "milestone:0.1.0"]
scope = ["CONTRIBUTING.md", "README.md"]

[[acceptance]]
text = "given branch protection, when a PR has green CI but no approval, then merge is blocked for non-bypass members"
bound = true
+++
