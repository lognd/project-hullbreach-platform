+++
id = "01M2H5T11QP42D39KC9ZNW0G2J"
title = "S17 Update ratings after a match"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T11JBHEEDN4QMJSPKR91"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0055"]
labels = ["jira:SCRUM-38", "owner:lognd", "milestone:0.2.0"]
scope = ["docs/index.md", "src/hullbreach_server/db/models/rating.py", "src/hullbreach_server/rating/elo.py", "src/hullbreach_server/services/matches.py", "tests/unit/test_elo.py", "tests/unit/test_rating_history.py"]

[[acceptance]]
text = "given a recorded match, when ratings update, then both change according to the documented formula"
bound = false

[[acceptance]]
text = "given any match, when ratings update, then the winner never loses rating and the loser never gains"
bound = false

[[acceptance]]
text = "given a rating change, when stored, then it is attached to the match so history can be reconstructed"
bound = false
+++

As a player, I want my rating to go up when I beat a stronger opponent and down less when I lose to one, so that the number reflects skill and not just play count.

Open questions:
- Plain Elo with a fixed K-factor, or a higher K for new accounts?
- Starting rating and floor?
- Do unranked / LAN matches affect rating? (Proposal: only matches on a trusted game server do.)
