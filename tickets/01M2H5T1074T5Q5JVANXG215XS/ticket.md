+++
id = "01M2H5T1074T5Q5JVANXG215XS"
title = "Alembic migrations with a hullbreach_server db upgrade command"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
points = 3
parent = "01M2H5T105AGGPXTV9ETEC5DF2"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:02Z"
aliases = ["T-0007"]
labels = ["jira:SCRUM-75", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/db/migrations/", "src/hullbreach_server/__main__.py", "tests/system/test_build.py", "alembic.ini", "pyproject.toml", "uv.lock", "docs/index.md", "design/hullbreach.strata", "frob.toml"]

[[acceptance]]
text = "given a fresh database, when the upgrade command runs, then alembic heads match the models"
bound = false
+++

## Reopen log
- 2026-09-16: PR #13 frob check failed with REF001/REF002/COV001/NEGEXIST001; fixing per coordinator direction
