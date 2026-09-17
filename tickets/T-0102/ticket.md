---
id: T-0102
title: Add a request timeout to web/src/api/auth.ts's fetch calls
state: queued
kind: feature
origin: human
created: '2026-09-16'
priority: medium
parent: null
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- web/src/api/auth.ts
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
T-0017 implemented register()/login()/logout()/fetchSession() in web/src/api/auth.ts without a request timeout (e.g. AbortController-based); design/hullbreach.strata's REL200:f_register/f_login_web/f_logout waivers were written expecting T-0017 to declare/prove one. Add a real timeout (AbortSignal.timeout or equivalent) to every fetch call in this file and update/remove the corresponding REL200 waivers on the browser node.