+++
id = "01M2H5T12R5AJV3F3ZWEPGM24D"
title = "S35 Save and load ship designs (platform half: design storage)"
type = "story"
category = "todo"
priority = "medium"
points = 3
parent = "01M2H5T12NSRFVQ2H4YCE7ZX30"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-09T04:05:31Z"
aliases = ["T-0088"]
labels = ["needs-game", "milestone:0.2.0"]
scope = ["src/hullbreach_server/api/designs.py", "src/hullbreach_server/db/models/design.py", "tests/unit/test_designs.py"]

[[acceptance]]
text = "given a named design, when saved and later loaded, then it round-trips unchanged"
bound = false

[[acceptance]]
text = "given a design that violates current rules, when loaded, then it is reported rather than silently altered"
bound = false
+++

As a player, I want to save a ship design and load it before a match, so that I do not rebuild from scratch every game.

Open questions:
- Local files, or stored on the platform under the account?
- Is a design validated on load against the current block rules?
