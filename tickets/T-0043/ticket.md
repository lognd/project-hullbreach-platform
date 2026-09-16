---
id: T-0043
title: S15 Navigate the site consistently
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0042
tier: story
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- web/src/App.tsx
- web/src/components/Footer.tsx
- web/src/components/Header.tsx
- web/src/router.tsx
- web/tests/unit/Header.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given any page, when signed out, then the header shows login and register;
    when signed in, then username, profile, store, and logout
  evidence: []
- text: given the keyboard alone, when navigating, then every link and control is
    reachable
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a player, I want the same header and footer on every page with login state, profile, and store links, so that I always know where I am and how to get anywhere else.

Open questions:
- Client-side routing library, or plain links between pages?
- Dark/light toggle, or is the dark cockpit theme the only theme?
