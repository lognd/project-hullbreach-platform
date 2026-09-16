---
id: T-0080
title: Admin set-rating endpoint writing a RatingChange with the admin's reason
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0079
tier: ticket
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/api/admin/ratings.py
- src/hullbreach_server/services/admin.py
- tests/unit/test_admin_ratings.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a set-rating call, when applied, then history shows the admin entry
    and the new rating
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
