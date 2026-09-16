---
id: T-0033
title: S10 Edit my account details
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0029
tier: story
sprint: sprint-2
runs_last: false
milestone: 0.2.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/me.py
- src/hullbreach_server/auth/sessions.py
- tests/unit/test_me_edit.py
- web/src/pages/Settings.tsx
- web/tests/unit/Settings.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given the current password, when email or password is changed, then it succeeds;
    without it, refused
  evidence: []
- text: given a display-name change, when submitted, then registration rules apply
  evidence: []
- text: given a password change, when it succeeds, then other active sessions are
    invalidated
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want to change my display name, email, and password, so that my account stays accurate and secure over time.

Open questions:
- Does changing the password require the current password? (Recommended yes.)
- Is the username changeable, or only a separate display name?
