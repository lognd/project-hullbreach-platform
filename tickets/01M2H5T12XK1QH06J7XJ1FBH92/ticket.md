+++
id = "01M2H5T12XK1QH06J7XJ1FBH92"
title = "S52 Watch a match from the website"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T12W9P6BA3BYVYJFFB4T"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0093"]
labels = ["needs-game", "jira:SCRUM-73", "owner:lognd"]
scope = ["src/hullbreach_server/api/replays.py", "tests/unit/test_replays.py", "web/src/pages/Replay.tsx"]

[[acceptance]]
text = "given a match page, when opened, then the match plays back with both ships and the arena"
bound = false
+++

As a visitor, I want to spectate a live or recorded match in the browser, so that I can see the game before installing it.

Open questions:
- Live relay from the game server, or replay from recorded inputs?
