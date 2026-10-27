+++
id = "01M5XCX8NS771W7TARY655HA78"
title = "Concurrent purchase test on real Postgres"
type = "task"
category = "todo"
priority = "medium"
reporter = "a-carten"
created = "2026-10-27T00:42:04Z"
updated = "2026-10-27T00:42:04Z"
scope = ["tests/unit/test_store_purchase_concurrent.py", "src/hullbreach_server/services/store.py", "docs/index.md", ".github/workflows/ci.yml", "changelog.d/**"]
+++

N parallel purchases must never overdraw or double-grant.
