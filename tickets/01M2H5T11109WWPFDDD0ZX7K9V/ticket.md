+++
id = "01M2H5T11109WWPFDDD0ZX7K9V"
title = "S10 Edit my account details"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T10XRAQYXM52JKK4FTSQ"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0033"]
labels = ["jira:SCRUM-31", "owner:lognd", "milestone:0.2.0"]
scope = ["src/hullbreach_server/api/me.py", "src/hullbreach_server/auth/sessions.py", "tests/unit/test_me_edit.py", "web/src/pages/Settings.tsx", "web/tests/unit/Settings.test.tsx"]

[[acceptance]]
text = "given the current password, when email or password is changed, then it succeeds; without it, refused"
bound = false

[[acceptance]]
text = "given a display-name change, when submitted, then registration rules apply"
bound = false

[[acceptance]]
text = "given a password change, when it succeeds, then other active sessions are invalidated"
bound = false
+++

As a player, I want to change my display name, email, and password, so that my account stays accurate and secure over time.

Open questions:
- Does changing the password require the current password? (Recommended yes.)
- Is the username changeable, or only a separate display name?
