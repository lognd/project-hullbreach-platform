+++
id = "01M2H5T10YFV60H1CQDEEH5164"
title = "S09 View my profile"
type = "story"
category = "todo"
priority = "medium"
points = 5
parent = "01M2H5T10XRAQYXM52JKK4FTSQ"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-09T04:05:30Z"
aliases = ["T-0030"]
labels = ["jira:SCRUM-30", "owner:a-carten", "milestone:0.2.0"]
scope = ["src/hullbreach_server/api/me.py", "src/hullbreach_server/services/profile.py", "tests/unit/test_me.py", "web/src/pages/Profile.tsx", "web/tests/unit/Profile.test.tsx"]

[[acceptance]]
text = "given a logged-in player, when they open their profile, then username, rating, currency, owned skins, and last five matches show"
bound = false

[[acceptance]]
text = "given a new match or purchase, when the profile loads, then it reflects the change without a code change or manual refresh of the database"
bound = false

[[acceptance]]
text = "given a phone-width screen, when the profile renders, then it is usable"
bound = false
+++

As a player, I want a profile page that shows my username, rating, currency, owned skins, and recent matches, so that I can see how I am doing at a glance.

Open questions:
- Public profile by username, or private to the owner?
- How many recent matches before linking to full history?
