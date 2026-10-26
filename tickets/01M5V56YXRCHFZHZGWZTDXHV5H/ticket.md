+++
id = "01M5V56YXRCHFZHZGWZTDXHV5H"
title = "One-command demo and front-to-back smoke test"
type = "task"
category = "done"
outcome = "done"
priority = "high"
reporter = "lognd"
created = "2026-10-26T03:49:05Z"
updated = "2026-10-26T04:37:46Z"
scope = ["src/hullbreach_ops/**", "tests/unit/test_ops_*.py", "Makefile", "README.md", "docs/index.md", "changelog.d/**"]
+++

Class demo: make demo brings up db, migrations, API, web and a demo account; make smoke checks register/login/me/session.
