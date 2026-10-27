+++
id = "01M5XZHXQ70E4GMKH145HZ18HV"
title = "demo-wipe: completely wipe the local stack between demo runs"
type = "task"
category = "todo"
priority = "high"
points = 3
reporter = "a-carten"
created = "2026-10-27T06:07:56Z"
updated = "2026-10-27T06:07:56Z"
labels = ["owner:lognd"]
scope = ["src/hullbreach_ops/**", "tests/unit/test_ops_*.py", "Makefile", "docs/demo-runbook.md", "docs/index.md", "changelog.d/**"]

[[acceptance]]
text = "given demo-wipe confirmed, when it runs, then the stack is stopped, the compose project's volumes removed and local logs cleared, and manual leftovers listed"
bound = false

[[acceptance]]
text = "given a mistyped confirmation, when demo-wipe runs, then nothing is deleted"
bound = false
+++

reset-db keeps .hullbreach/logs, and make console replays old api.log lines, so old usernames reappear after a DB wipe.
