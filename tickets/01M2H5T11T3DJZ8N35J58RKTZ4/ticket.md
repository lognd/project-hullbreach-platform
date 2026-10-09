+++
id = "01M2H5T11T3DJZ8N35J58RKTZ4"
title = "S18 Browse my match history"
type = "story"
category = "todo"
priority = "medium"
points = 5
parent = "01M2H5T11JBHEEDN4QMJSPKR91"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-09T04:05:31Z"
aliases = ["T-0058"]
labels = ["jira:SCRUM-39", "owner:a-carten", "milestone:0.2.0"]
scope = ["src/hullbreach_server/api/me.py", "src/hullbreach_server/services/matches.py", "tests/unit/test_me_matches.py", "web/src/pages/History.tsx", "web/tests/unit/History.test.tsx"]

[[acceptance]]
text = "given a player, when history is fetched, then matches are newest first with opponent, win/loss, date, duration, rating before and after, and stats"
bound = false

[[acceptance]]
text = "given hundreds of matches, when the list renders, then it stays responsive"
bound = false
+++

As a player, I want a list of my past matches with opponent, result, rating change, and stats, so that I can see what worked and what did not.

Open questions:
- Pagination or infinite scroll? How many per page?
- Can a player open an opponent's history from a match row?
