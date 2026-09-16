---
id: T-0036
title: S11 Delete my account
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
- src/hullbreach_server/services/account_deletion.py
- tests/unit/test_me_delete.py
- web/src/pages/Settings.tsx
- web/tests/unit/Settings.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given an explicit confirmation step, when a player deletes their account,
    then it is deleted
  evidence: []
- text: given a deleted account, when its credentials are used or its profile requested,
    then both fail
  evidence: []
- text: given a deleted player, when an opponent views history, then the match still
    shows with the player anonymized
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want to permanently delete my account, so that I can leave the game and take my data with me.

Open questions:
- Hard delete, or anonymize and keep match records so opponents' histories stay intact?
- Grace period / undo, or immediate?
