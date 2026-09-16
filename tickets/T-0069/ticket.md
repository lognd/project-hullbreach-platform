---
id: T-0069
title: S21 Earn currency by playing
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0064
tier: story
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/db/models/ledger.py
- src/hullbreach_server/services/currency.py
- src/hullbreach_server/services/matches.py
- tests/unit/test_currency.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a recorded match, when it is saved, then both players' balances increase
    by the documented amounts
  evidence: []
- text: given a profile, when the balance shows, then it equals recorded earnings
    minus purchases
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want to earn in-game currency for completing matches, more for winning, so that playing is how I unlock cosmetics.

Open questions:
- Payout per match, per win, per first win of the day? Any cap to discourage farming?
- Do LAN matches pay out?
