+++
id = "01M2H5T10WP2DH6ZHDRPYGEZBF"
title = "Role enum on User, require_admin dependency returning 403, and role excluded from register/profile schemas"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
points = 2
parent = "01M2H5T10VN6HGPSN5F492TGYA"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:02Z"
aliases = ["T-0028"]
labels = ["jira:SCRUM-95", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/db/models/user.py", "src/hullbreach_server/auth/deps.py", "src/hullbreach_server/auth/schemas.py", "tests/unit/test_roles.py", "docs/index.md", "src/hullbreach_server/db/migrations/versions/*.py", "src/hullbreach_server/db/models/session.py"]

[[acceptance]]
text = "given a Player token, when an admin route is called, then 403 with a permissions message"
bound = false
+++
