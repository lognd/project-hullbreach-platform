+++
id = "01M2H5T11XDV04575V7T3S9A68"
title = "S19 See where I stand"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T11JBHEEDN4QMJSPKR91"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0061"]
labels = ["jira:SCRUM-40", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/leaderboard.py", "src/hullbreach_server/services/leaderboard.py", "tests/unit/test_leaderboard.py", "web/src/pages/Leaderboard.tsx", "web/tests/unit/Leaderboard.test.tsx"]

[[acceptance]]
text = "given any visitor, when the leaderboard loads, then rank, name, rating, and matches played show for the top players"
bound = false

[[acceptance]]
text = "given a logged-in player outside the visible range, when the leaderboard loads, then their own rank shows"
bound = false
+++

As a player, I want a leaderboard of the top-rated players, so that I have someone to aim for.

Open questions:
- Top 100 only, or paginated? Show players with fewer than N matches?
