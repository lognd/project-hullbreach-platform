+++
id = "01M2H5T12BT56ETFWBMD8MR8HR"
title = "S23 Look up and moderate a player"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T12AMDB83JD0BVTR1BQP"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0075"]
labels = ["jira:SCRUM-44", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/admin/players.py", "src/hullbreach_server/api/auth.py", "src/hullbreach_server/db/models/moderation.py", "src/hullbreach_server/services/admin.py", "tests/unit/test_admin_players.py", "tests/unit/test_moderation.py", "web/src/pages/admin/Players.tsx", "web/src/router.tsx", "web/tests/unit/AdminPlayers.test.tsx"]

[[acceptance]]
text = "given a username or email, when an admin searches, then they see the profile, matches, and trust events"
bound = false

[[acceptance]]
text = "given a player, when an admin suspends them, then the player cannot log in and sees why; reinstate reverses it"
bound = false

[[acceptance]]
text = "given any moderation action, when performed, then admin, time, and reason are recorded"
bound = false

[[acceptance]]
text = "given a Player session, when any admin screen or endpoint is requested, then it is refused"
bound = false
+++

As a administrator, I want to search for a player and suspend or reinstate their account, so that I can act on cheating or abuse reports.

Open questions:
- Suspension: time-boxed or indefinite? Does it block login, ranked play, or both?
- Record a reason and who did it?
