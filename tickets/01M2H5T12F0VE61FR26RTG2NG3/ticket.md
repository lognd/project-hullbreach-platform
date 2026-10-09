+++
id = "01M2H5T12F0VE61FR26RTG2NG3"
title = "S24 Correct a player's rating"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T12AMDB83JD0BVTR1BQP"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0079"]
labels = ["jira:SCRUM-45", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/admin/matches.py", "src/hullbreach_server/api/admin/ratings.py", "src/hullbreach_server/services/admin.py", "src/hullbreach_server/services/matches.py", "tests/unit/test_admin_ratings.py", "tests/unit/test_admin_void.py"]

[[acceptance]]
text = "given a rating value and reason, when an admin sets it, then the change appears in the player's rating history with the reason"
bound = false

[[acceptance]]
text = "given a recorded match, when an admin voids it, then its rating and currency effects are reversed for both players"
bound = false
+++

As a administrator, I want to reset or adjust a player's rating, so that I can undo the effect of a cheated or bugged match.

Open questions:
- Adjust to a specific value, or only reset to the starting rating?
- Should voiding a match automatically re-run the rating change for both players?
