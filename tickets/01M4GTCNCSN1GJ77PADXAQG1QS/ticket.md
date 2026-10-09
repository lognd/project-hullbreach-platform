+++
id = "01M4GTCNCSN1GJ77PADXAQG1QS"
title = "Postgres-backed integration tests for the db boundary"
type = "bug"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T17:11:51Z"
updated = "2026-10-09T17:11:51Z"
labels = ["owner:lognd", "audit:db"]
scope = ["tests/system/test_postgres.py"]
+++

found while working ~7523D2D: the role CHECK and case-insensitive unique indexes are now covered on SQLite only. The production dialect (Postgres: seed postgresql insert branch, timestamptz, FK cascade, server_default, DataError on over-long values, concurrent register race) has no integration coverage. Add a Postgres-backed integration test (testcontainers or a CI service) that runs upgrade head, seeds twice, and round-trips register/login/session.
