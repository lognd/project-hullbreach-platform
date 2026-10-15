+++
id = "01M2H5T112QT3VM0NV9VXKXM6B"
title = "PATCH /api/v1/me with current-password confirmation and session invalidation on password change"
type = "task"
category = "in-progress"
priority = "medium"
points = 2
parent = "01M2H5T11109WWPFDDD0ZX7K9V"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-15T14:51:18Z"
aliases = ["T-0034"]
labels = ["jira:SCRUM-147", "owner:lognd", "milestone:0.2.0", "creates:tests/unit/test_me_edit.py"]
scope = ["src/hullbreach_server/api/me.py", "src/hullbreach_server/auth/sessions.py", "tests/unit/test_me_edit.py", "src/hullbreach_server/auth/__init__.py", "src/hullbreach_server/auth/schemas.py", "docs/index.md", "tests/unit/test_sessions.py"]

[[acceptance]]
text = "given a password change, when it succeeds, then every other session for that user is revoked"
bound = false
+++
