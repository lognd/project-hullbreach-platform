+++
id = "01M5V93V80GQXC4283VFZPEYH7"
title = "ensure_env/.env.example hardcode 5432 in HULLBREACH_DATABASE_URL"
type = "bug"
category = "todo"
priority = "medium"
reporter = "a-carten"
created = "2026-10-26T04:57:17Z"
updated = "2026-10-26T05:07:37Z"
scope = ["src/hullbreach_ops/demo.py", ".env.example"]

[[acceptance]]
text = "Given HULLBREACH_DB_PORT is set, when ensure_env writes .env, then the database URL uses that port"
bound = true
+++

found while landing PR 45: HULLBREACH_DB_PORT=15432 leaves HULLBREACH_DATABASE_URL pointing at localhost:5432, so a demo on a non-default DB port connects to the wrong database. ensure_env should derive the URL port from HULLBREACH_DB_PORT (and CORS origin from HULLBREACH_WEB_PORT).
