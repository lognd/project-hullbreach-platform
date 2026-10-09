+++
id = "01M2H5T126K37TGJQ32PYKEHW6"
title = "Currency ledger model and payout rules applied on match record"
type = "task"
category = "todo"
priority = "medium"
points = 3
parent = "01M2H5T125F6FYMXJ9JZXSYE6W"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0070"]
labels = ["jira:SCRUM-184", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/db/models/ledger.py", "src/hullbreach_server/services/currency.py", "src/hullbreach_server/services/matches.py", "tests/unit/test_currency.py"]

[[acceptance]]
text = "given a win and a loss, when recorded, then the winner's credit exceeds the loser's and both are positive"
bound = false

[[acceptance]]
text = "given the ledger, when the balance is derived, then it equals the sum of entries"
bound = false
+++
