+++
id = "01M2H5T10EF0AKZ2JZC55N747C"
title = "S04 Register a new account"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T10DT4023PZH1JHFEWQE"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0014"]
labels = ["jira:SCRUM-25", "owner:lognd", "milestone:0.1.0"]
scope = ["src/hullbreach_server/api/auth.py", "src/hullbreach_server/auth/passwords.py", "src/hullbreach_server/auth/schemas.py", "src/hullbreach_server/db/models/user.py", "tests/unit/test_auth_register.py", "tests/unit/test_passwords.py", "web/src/api/auth.ts", "web/src/pages/Register.tsx", "web/tests/unit/Register.test.tsx"]

[[acceptance]]
text = "given a unique username, email, and password, when a visitor registers from the website, then an account is created"
bound = false

[[acceptance]]
text = "given a taken username or email or a short password, when registering, then it is refused with a specific message"
bound = false

[[acceptance]]
text = "given any code path, when a password is handled, then it is never stored or logged in plain text"
bound = false

[[acceptance]]
text = "given a new account, when it is created, then it has the Player role, zero currency, and the starting rating"
bound = false
+++

As a new player, I want to create an account with a username, email, and password, so that my ships, rating, and purchases are mine and follow me between machines.

Open questions:
- Verify email addresses, or accept unverified for the course?
- Username rules: length, allowed characters, profanity filter?
- Minimum password rules: length floor only, or a breached-password check?
