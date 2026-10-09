+++
id = "01M3DG5Y3XW56W6Y8AFP4ZPA60"
title = "S04-4: Tests for duplicate username/email and short-password rejection"
type = "task"
category = "todo"
priority = "critical"
points = 2
parent = "01M2H5T10EF0AKZ2JZC55N747C"
reporter = "human"
created = "2026-09-26T00:00:00Z"
updated = "2026-10-09T04:06:46Z"
aliases = ["T-0125"]
labels = ["platform", "web", "jira:SCRUM-89", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/api/auth.py", "src/hullbreach_server/auth/passwords.py", "src/hullbreach_server/auth/schemas.py", "src/hullbreach_server/db/models/user.py", "tests/unit/test_auth_register.py", "tests/unit/test_passwords.py", "web/src/api/auth.ts", "web/src/pages/Register.tsx", "web/tests/unit/Register.test.tsx"]

[[acceptance]]
text = "Given an existing username or email, when a second account registers with it, then the API answers 409 naming the offending field"
bound = true

[[acceptance]]
text = "Given a password shorter than 8 characters, when an account registers, then the API answers 422"
bound = true
+++

https://aliens-against-humanity.atlassian.net/browse/SCRUM-89

Tests for duplicate username/email and short-password rejection
Parent story: SCRUM-25
