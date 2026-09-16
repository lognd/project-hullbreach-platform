---
id: T-0070
title: Currency ledger model and payout rules applied on match record
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0069
tier: ticket
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
- text: given a win and a loss, when recorded, then the winner's credit exceeds the
    loser's and both are positive
  evidence: []
- text: given the ledger, when the balance is derived, then it equals the sum of entries
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
