---
id: T-draft-31a477af
title: 'S04-4: Tests for duplicate username/email and short-password rejection'
state: queued
kind: feature
origin: human
created: '2026-09-26'
priority: critical
parent: T-0014
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
flavour: null
due: null
rank: null
points: null
unsized_ack: false
unsized_ack_reason: null
tokens_in: null
tokens_out: null
tokens_cache_read: null
usage: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
worktree: null
branch: null
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
threat: null
component: null
labels:
- platform
- web
- jira:SCRUM-89
- owner:lognd
anchor: false
anchor_reason: null
land_commit: null
---
https://aliens-against-humanity.atlassian.net/browse/SCRUM-89

Tests for duplicate username/email and short-password rejection
Parent story: SCRUM-25