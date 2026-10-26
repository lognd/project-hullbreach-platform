+++
id = "01M5VJK6MN84BGJE2C7BJAHWAT"
title = "First make demo fails with non-default HULLBREACH_DB_PORT"
type = "bug"
category = "todo"
priority = "medium"
reporter = "a-carten"
created = "2026-10-26T07:42:57Z"
updated = "2026-10-26T08:12:53Z"
scope = ["src/hullbreach_ops/**", "tests/unit/test_ops_demo.py", "docs/demo-script.md"]
+++

found while working 01M5VJFGZBNSTESCDC81QKCGHQ. Fresh checkout with HULLBREACH_DB_PORT=15432 exported: demo generates its settings file with the right port and starts the container, then prepare_db connects to localhost:5432 (config likely cached before the file existed). A second make demo works.
