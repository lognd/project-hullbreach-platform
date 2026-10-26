+++
id = "01M5W2589RQ8Y6MAAMNA32EHF9"
title = "Leaderboard page polls every 5s while visible"
type = "task"
category = "todo"
priority = "medium"
reporter = "a-carten"
created = "2026-10-26T12:14:57Z"
updated = "2026-10-26T12:21:15Z"
scope = ["web/src/pages/Leaderboard.tsx", "web/tests/unit/Leaderboard.test.tsx", "docs/index.md", "docs/demo-script.md"]
+++

Demo hardening: the open Leaderboard fetched once, so the 4:15 demo step needed a re-click. Poll silently every 5s while the tab is visible, clean up on unmount.
