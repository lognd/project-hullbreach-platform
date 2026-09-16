---
id: T-0018
title: S05 Log in and stay logged in
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
- src/hullbreach_server/auth/deps.py
- src/hullbreach_server/auth/sessions.py
- src/hullbreach_server/db/models/session.py
- tests/unit/test_auth_login.py
- tests/unit/test_sessions.py
- web/src/auth/session.ts
- web/src/pages/Login.tsx
- web/tests/unit/Login.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given correct credentials, when logging in, then a session is issued; given
    incorrect ones, then a generic refusal
  evidence: []
- text: given a logged-in player, when the page is refreshed, then they stay signed
    in until the session expires
  evidence: []
- text: given a session, when its configured period passes or it is revoked server-side,
    then it is rejected
  evidence: []
- text: given any response or redirect, when inspected, then no session token appears
    in a URL
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want to log in with my username or email and password and remain signed in across page loads, so that I do not have to re-enter credentials every time I open the site.

Open questions:
- Session length: hours, days, or until logout? Remember me?
- Token transport: HTTP-only cookie for the website versus bearer header for the game client, or bearer everywhere?
- Rate limiting on failed logins?
