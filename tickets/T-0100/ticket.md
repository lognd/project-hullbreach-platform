---
id: T-0100
title: Wire GET /api/v1/ready into a real caller (web/ops)
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
- web/src/**
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
body_changes:
- mode: append
  reason: T-0012 close requires re-pointing three REL200 waivers off itself; consolidating
    them onto this already-open successor rather than filing three more tickets
  actor: logan
  at: '2026-09-16'
  old_length: 227
  new_length: 756
designated_repro_test: null
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
found while working T-0012: the readiness route (GET /api/v1/ready) has no caller outside its own tests yet (WIRE001 waived on T-0012 pending this). Wire it into the web app's health/status check or ops tooling once one exists.

Also covers wiring /api/v1/health into the same web/ops caller (both routes previously had no caller besides tests), and is the successor for design/hullbreach.strata's REL200:f_health, REL200:f_ready, and REL200:f_api_to_db waivers re-pointed off T-0012 at close: once this ticket adds a real caller with a real request timeout, it declares/proves the corresponding strata timeout attrs (create_db_engine already sets a 5s connect_timeout for the api->db call; formally declaring it in strata is this ticket's remaining work).