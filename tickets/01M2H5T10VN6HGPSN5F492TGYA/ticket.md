+++
id = "01M2H5T10VN6HGPSN5F492TGYA"
title = "S08 Distinguish administrators from players"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T10DT4023PZH1JHFEWQE"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0027"]
labels = ["jira:SCRUM-29", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/auth/deps.py", "src/hullbreach_server/auth/schemas.py", "src/hullbreach_server/db/models/user.py", "tests/unit/test_roles.py"]

[[acceptance]]
text = "given any account, when inspected, then it has exactly one role, Player or Administrator"
bound = false

[[acceptance]]
text = "given an admin-only endpoint, when a Player session calls it, then 403 with a permissions error"
bound = false

[[acceptance]]
text = "given the register and profile-edit paths, when a role is supplied, then it is ignored or refused"
bound = false
+++

As a administrator, I want my account to carry an Administrator role that ordinary accounts cannot grant themselves, so that moderation actions are only available to the team.

Open questions:
- How is the first admin created: seed script, environment variable, or database promotion?
- Can an admin promote other admins from the UI, or only via seed?
