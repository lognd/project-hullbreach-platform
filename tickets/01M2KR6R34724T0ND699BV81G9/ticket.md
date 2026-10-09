+++
id = "01M2KR6R34724T0ND699BV81G9"
title = "Wire GET /api/v1/ready into a real caller (web/ops)"
type = "task"
category = "todo"
priority = "medium"
reporter = "human"
created = "2026-09-16T00:00:00Z"
updated = "2026-09-16T00:00:00Z"
aliases = ["T-0100"]
labels = ["jira:none"]
scope = ["web/src/**"]
+++

found while working T-0012: the readiness route (GET /api/v1/ready) has no caller outside its own tests yet (WIRE001 waived on T-0012 pending this). Wire it into the web app's health/status check or ops tooling once one exists.

Also covers wiring /api/v1/health into the same web/ops caller (both routes previously had no caller besides tests), and is the successor for design/hullbreach.strata's REL200:f_health, REL200:f_ready, and REL200:f_api_to_db waivers re-pointed off T-0012 at close: once this ticket adds a real caller with a real request timeout, it declares/proves the corresponding strata timeout attrs (create_db_engine already sets a 5s connect_timeout for the api->db call; formally declaring it in strata is this ticket's remaining work).
