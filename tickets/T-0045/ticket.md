---
id: T-0045
title: S13 Learn what the game is from the landing page
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
- web/src/pages/Landing.tsx
- web/tests/unit/Landing.test.tsx
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given the landing page, when it loads, then one screen explains the premise
    and links to register, log in, and download
  evidence: []
- text: given phone, tablet, and desktop widths, when rendered, then the layout is
    correct
  evidence: []
- text: given crunk check, when run on the page, then every color and spacing value
    comes from the design system
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
As a visitor, I want a landing page that explains the game and shows how to get it, so that I can decide whether to make an account.

Open questions:
- Where does the download link point: GitHub release, itch.io, or a file on the platform host?
- Live stats (players online, matches today) on the landing page?
