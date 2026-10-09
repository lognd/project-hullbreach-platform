+++
id = "01M2H5T12PWAJEVZ18CDFJCG57"
title = "S29 Find an online opponent (platform half: matchmaking queue API)"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T12NSRFVQ2H4YCE7ZX30"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0086"]
labels = ["needs-game", "milestone:0.2.0"]
scope = ["src/hullbreach_server/api/matchmaking.py", "src/hullbreach_server/services/matchmaking.py", "tests/unit/test_matchmaking.py"]

[[acceptance]]
text = "given a signed-in player, when they enter the queue, then they can see they are queued and cancel"
bound = false

[[acceptance]]
text = "given two queued players within the rating window, when matched, then both receive the same game server address without typing one"
bound = false

[[acceptance]]
text = "given a matched game, when it ends, then it is recorded as ranked"
bound = false
+++

As a player, I want to queue for a ranked match and be paired with an opponent of similar rating, so that matches are fair and I do not have to arrange them myself.

Open questions:
- Who runs matchmaking: the platform API, or a lobby service on the game server host?
- Widening rating window over time in queue? Maximum wait before matching anyone?
- How many game servers do we run, and where?
