+++
id = "01M2H5T12YR0X3X58JHWX0FPAB"
title = "Replay ingestion endpoint and match replay page (design spike first)"
type = "task"
category = "todo"
priority = "medium"
points = 5
parent = "01M2H5T12XK1QH06J7XJ1FBH92"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0094"]
labels = ["needs-game", "jira:SCRUM-215", "owner:lognd"]
scope = ["src/hullbreach_server/api/replays.py", "web/src/pages/Replay.tsx", "tests/unit/test_replays.py"]

[[acceptance]]
text = "given a recorded input log, when uploaded, then the replay page renders both ships"
bound = false
+++
