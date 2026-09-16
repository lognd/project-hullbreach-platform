---
id: T-draft-8d975dbc
title: test_register_response_never_exposes_password_hash xpasses once db/ fixtures
  resolve
state: queued
kind: bug
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
- tests/unit/test_auth_register.py
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
found while working T-0006: this T-0016 xfail(strict=True) test previously failed at fixture setup (ImportError on hullbreach_server.db, which did not exist). Now that T-0006 lands db/, the app/client fixtures succeed, the request 404s (no /register route yet), and the response body {"detail": "Not Found"} incidentally satisfies 'password_hash not in body' and 'password not in body', causing an XPASS(strict) failure in CI (server (python) job on PR #10). The assertions need to also check for a real 2xx/4xx-with-validation-shape response, or the test needs a route-exists guard, so it keeps failing for the right reason until T-0016 lands the real endpoint.