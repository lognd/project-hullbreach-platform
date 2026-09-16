---
id: T-0013
title: E2 Accounts and authentication
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: high
parent: null
tier: epic
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/auth.py
- src/hullbreach_server/auth/deps.py
- src/hullbreach_server/auth/passwords.py
- src/hullbreach_server/auth/schemas.py
- src/hullbreach_server/auth/sessions.py
- src/hullbreach_server/db/models/session.py
- src/hullbreach_server/db/models/user.py
- tests/unit/test_auth_game.py
- tests/unit/test_auth_login.py
- tests/unit/test_auth_logout.py
- tests/unit/test_auth_register.py
- tests/unit/test_passwords.py
- tests/unit/test_roles.py
- tests/unit/test_sessions.py
- web/src/api/auth.ts
- web/src/auth/session.ts
- web/src/components/Header.tsx
- web/src/pages/Login.tsx
- web/src/pages/Register.tsx
- web/tests/unit/Header.test.tsx
- web/tests/unit/Login.test.tsx
- web/tests/unit/Register.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
Epic from the Module 4 story map. Stories:
- S04 Register a new account
- S05 Log in and stay logged in
- S06 Log out
- S07 Sign in from inside the game
- S08 Distinguish administrators from players
