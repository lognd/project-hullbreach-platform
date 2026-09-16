---
id: T-0025
title: S07 Sign in from inside the game
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
- tests/unit/test_auth_game.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given website credentials, when used from the game client, then sign-in succeeds
  evidence: []
- text: given a signed-in client, when it joins a match, then the game server can
    validate the session with the API
  evidence: []
- text: given a signed-out client, when building ships offline, then it works, but
    ranked matches are refused
  evidence: []
threat: null
component: null
labels:
- needs-game
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want to sign into my platform account from the game client, so that my matches count toward my rating and my skins appear on my ship.

Open questions:
- Username/password form in the game, or open the website and receive a token (device-code style)?
- How does the game client store the token between launches?
