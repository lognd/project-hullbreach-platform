+++
id = "01M2H5T11NHABAJEYKDDDK3JZ3"
title = "Match and MatchPlayerStats models with migration"
type = "task"
category = "in-progress"
priority = "medium"
points = 2
parent = "01M2H5T11KNPF6MRRJKJR6793R"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-09T04:04:34Z"
aliases = ["T-0053"]
labels = ["needs-game", "jira:SCRUM-137", "owner:lognd", "milestone:0.2.0"]
scope = ["src/hullbreach_server/db/models/match.py", "src/hullbreach_server/db/migrations/", "tests/unit/test_match_models.py", "src/hullbreach_server/db/models/__init__.py", "docs/index.md"]

[[acceptance]]
text = "given a match with two players, when saved, then both stat rows reference it"
bound = false

[[acceptance]]
text = "Given a fresh database, when the Alembic migrations run to head, then the matches and match_player_stats tables exist and match the declarative models"
bound = false

[[acceptance]]
text = "Given a match, when a second stat row is saved for the same player, then the database rejects it"
bound = false
+++
