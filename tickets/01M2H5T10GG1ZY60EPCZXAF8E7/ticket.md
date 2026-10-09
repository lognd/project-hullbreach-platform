+++
id = "01M2H5T10GG1ZY60EPCZXAF8E7"
title = "POST /api/v1/auth/register with username, email, and password validation"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
points = 3
parent = "01M2H5T10EF0AKZ2JZC55N747C"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:02Z"
aliases = ["T-0016"]
labels = ["jira:SCRUM-87", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/api/auth.py", "src/hullbreach_server/auth/schemas.py", "tests/unit/test_auth_register.py", "src/hullbreach_server/api/__init__.py", "pyproject.toml", "uv.lock", "tests/unit/test_roles.py", "docs/index.md", "design/hullbreach.strata", "docs/design/sprint-1.md", "src/hullbreach_server/db/models/user.py"]

[[acceptance]]
text = "given a duplicate username, when registering, then 409 with a field-specific message"
bound = false

[[acceptance]]
text = "given a valid request, when registering, then 201 and role Player, currency 0, rating default"
bound = false
+++
