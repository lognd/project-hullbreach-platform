---
id: T-0047
title: S14 Understand what data is collected
state: queued
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0042
tier: story
sprint: sprint-3
runs_last: false
milestone: 0.3.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- web/src/components/CookieNotice.tsx
- web/src/components/Footer.tsx
- web/src/pages/DataPolicy.tsx
- web/tests/unit/CookieNotice.test.tsx
- web/tests/unit/DataPolicy.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a first-time visitor, when the site loads, then a dismissible cookie
    notice shows and does not return on that browser
  evidence: []
- text: given any page footer, when the data policy link is followed, then the page
    lists what is stored, why, and how to delete it
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a visitor, I want a cookie notice and a data policy page, so that I know what the site stores about me before I sign up.

Open questions:
- Do we set any non-essential cookies at all? If not, the notice can be informational rather than consent-gated.
- Who writes the policy text: the team, or adapt a template?
