+++
id = "01M2H5T10TQVP5A2R1N2S5Y3FP"
title = "Bearer-token login for the game client and GET /api/v1/auth/session for server-side validation"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
points = 2
parent = "01M2H5T10SJRRFCSNHGH9AF0ZF"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:02Z"
aliases = ["T-0026"]
labels = ["needs-game", "jira:SCRUM-99", "owner:lognd", "milestone:0.1.0"]
scope = ["tests/unit/test_auth_game.py", "docs/index.md", "design/hullbreach.strata", "src/hullbreach_server/db/migrations/versions/*.py", "src/hullbreach_server/db/models/session.py", "web/src/api/auth.ts"]

[[acceptance]]
text = "given a client token, when the game server calls the session endpoint, then it gets the player id and role"
bound = false
+++
