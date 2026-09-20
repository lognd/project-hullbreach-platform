---
id: T-draft-4377d950
title: 'Leave teammate breadcrumbs: pick-up guide and frob:todo markers at every plug-in
  point'
state: queued
kind: docs
origin: human
created: '2026-09-20'
priority: high
parent: null
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- docs/picking-up-work.md
- README.md
- CONTRIBUTING.md
- docs/index.md
- src/hullbreach_server/api/__init__.py
- src/hullbreach_server/db/models/__init__.py
- src/hullbreach_server/api/auth.py
- web/src/router.tsx
- web/src/App.tsx
- web/src/components/Footer.tsx
- web/src/api/auth.ts
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a new teammate, when they read docs/picking-up-work.md, then they can
    claim a queued ticket and know which file and example to start from
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
Sprint 1 landed as one author. The remaining backlog (T-0031 onward) is where teammates pick up. Leave a lane-by-lane pick-up guide and a frob:todo T-#### marker at each code site a queued ticket plugs into, so the next person landing in a file sees which ticket owns the gap.