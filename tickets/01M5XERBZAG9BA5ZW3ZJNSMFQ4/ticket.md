+++
id = "01M5XERBZAG9BA5ZW3ZJNSMFQ4"
title = "Demo rehearsal: narrate store purchase and equip on the console, verified runbook"
type = "bug"
category = "todo"
priority = "high"
reporter = "a-carten"
created = "2026-10-27T01:14:21Z"
updated = "2026-10-27T01:14:21Z"
scope = ["src/hullbreach_server/services/store.py", "src/hullbreach_server/services/equip.py", "tests/unit/test_service_events.py", "docs/demo-runbook.md", "docs/demo-script.md", "docs/index.md"]

[[acceptance]]
text = "given a successful purchase or equip, when console --db runs, then a DB line names the item and balance"
bound = false
+++

Found in the full demo rehearsal: buy and equip changed the database but printed no DB line.
