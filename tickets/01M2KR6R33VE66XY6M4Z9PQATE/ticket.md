+++
id = "01M2KR6R33VE66XY6M4Z9PQATE"
title = "Wire check_connectivity into App startup for fail-fast DB check"
type = "task"
category = "done"
outcome = "done"
priority = "medium"
reporter = "human"
created = "2026-09-16T00:00:00Z"
updated = "2026-09-16T00:00:02Z"
aliases = ["T-0099"]
labels = ["jira:none"]
scope = ["src/hullbreach_server/app/app.py", "tests/unit/test_app.py", "design/hullbreach.strata", "docs/design/sprint-1.md", "docs/index.md"]
+++

found while working T-0006: create_db_engine/check_connectivity exist per design D2, but App.__call__ does not call check_connectivity before uvicorn.run yet. This ticket wires that call and adds the test for it (docs/design/sprint-1.md section 3, decision D2).
