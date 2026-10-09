+++
id = "01M2H5T10ZV4EV17ZMHTQ455KJ"
title = "GET /api/v1/me aggregating profile, balance, inventory, and last five matches"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T10YFV60H1CQDEEH5164"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0031"]
labels = ["jira:SCRUM-145", "owner:lognd", "milestone:0.2.0"]
scope = ["src/hullbreach_server/api/me.py", "src/hullbreach_server/services/profile.py", "tests/unit/test_me.py"]

[[acceptance]]
text = "given a player with matches and items, when GET /me is called, then all five sections are present"
bound = false
+++
