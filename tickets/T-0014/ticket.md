---
id: T-0014
title: S04 Register a new account
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0013
tier: story
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/auth.py
- src/hullbreach_server/auth/passwords.py
- src/hullbreach_server/auth/schemas.py
- src/hullbreach_server/db/models/user.py
- tests/unit/test_auth_register.py
- tests/unit/test_passwords.py
- web/src/api/auth.ts
- web/src/pages/Register.tsx
- web/tests/unit/Register.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a unique username, email, and password, when a visitor registers from
    the website, then an account is created
  evidence: []
- text: given a taken username or email or a short password, when registering, then
    it is refused with a specific message
  evidence: []
- text: given any code path, when a password is handled, then it is never stored or
    logged in plain text
  evidence: []
- text: given a new account, when it is created, then it has the Player role, zero
    currency, and the starting rating
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a new player, I want to create an account with a username, email, and password, so that my ships, rating, and purchases are mine and follow me between machines.

Open questions:
- Verify email addresses, or accept unverified for the course?
- Username rules: length, allowed characters, profanity filter?
- Minimum password rules: length floor only, or a breached-password check?
