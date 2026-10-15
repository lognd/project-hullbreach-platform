+++
id = "01M2H5T10ZV4EV17ZMHTQ455KJ"
title = "GET /api/v1/me aggregating profile, balance, inventory, and last five matches"
type = "task"
category = "in-progress"
priority = "medium"
points = 2
parent = "01M2H5T10YFV60H1CQDEEH5164"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-15T14:48:34Z"
aliases = ["T-0031"]
labels = ["jira:SCRUM-145", "owner:lognd", "milestone:0.2.0", "creates:src/hullbreach_server/services/__init__.py", "creates:src/hullbreach_server/services/matches.py", "creates:tests/system/test_account_flow.py", "creates:src/hullbreach_server/api/me.py", "creates:src/hullbreach_server/services/profile.py", "creates:tests/unit/test_me.py"]
scope = ["src/hullbreach_server/api/me.py", "src/hullbreach_server/services/profile.py", "tests/unit/test_me.py", "src/hullbreach_server/api/__init__.py", "docs/index.md", "src/hullbreach_server/services/__init__.py", "src/hullbreach_server/services/matches.py", "tests/system/test_account_flow.py"]

[[acceptance]]
text = "given a player with matches and items, when GET /me is called, then all five sections are present"
bound = false
+++
