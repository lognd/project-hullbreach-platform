+++
id = "01M2H5T10PSWBJQ94G2ER5HP1H"
title = "S06 Log out"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T10DT4023PZH1JHFEWQE"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0022"]
labels = ["jira:SCRUM-27", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/api/auth.py", "tests/unit/test_auth_logout.py", "web/src/components/Header.tsx", "web/tests/unit/Header.test.tsx"]

[[acceptance]]
text = "given a logged-in player, when they log out from any page, then they land on the landing page"
bound = false

[[acceptance]]
text = "given a logout, when the previous token is used, then the API rejects it"
bound = false
+++

As a player, I want to log out from any page, so that the next person at this computer cannot act as me.

Open questions:
- Log out of this device only, or all devices?
