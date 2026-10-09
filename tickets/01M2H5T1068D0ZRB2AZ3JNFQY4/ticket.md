+++
id = "01M2H5T1068D0ZRB2AZ3JNFQY4"
title = "Database engine and session dependency from HULLBREACH_DATABASE_URL, fail fast at startup"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
points = 3
parent = "01M2H5T105AGGPXTV9ETEC5DF2"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:02Z"
aliases = ["T-0006"]
labels = ["jira:SCRUM-74", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/db/__init__.py", "src/hullbreach_server/db/engine.py", "tests/unit/test_db_engine.py", "docs/index.md", "pyproject.toml", "uv.lock", "tests/unit/conftest.py", "tests/system/test_build.py", "tests/unit/test_auth_register.py", "docs/design/registry/capability-via-ratchet.lock.json", "docs/design/sprint-1.md", "design/hullbreach.strata"]

[[acceptance]]
text = "given an unreachable database URL, when create_app starts, then startup fails with a message naming the host"
bound = false
+++

## Reopen log
- 2026-09-16: PR #10 CI red from fixture-activation ripple (I001 in conftest.py/test_build.py, XPASS in test_auth_register.py); coordinator directed fixing these inside T-0006 instead of via drafts
