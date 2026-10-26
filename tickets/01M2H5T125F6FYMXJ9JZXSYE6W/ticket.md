+++
id = "01M2H5T125F6FYMXJ9JZXSYE6W"
title = "S21 Earn currency by playing"
type = "story"
category = "in-progress"
priority = "medium"
parent = "01M2H5T1205GXC7WDK3G949GYJ"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-26T11:20:12Z"
aliases = ["T-0069"]
labels = ["jira:SCRUM-42", "owner:lognd", "milestone:0.3.0", "creates:src/hullbreach_server/db/migrations/versions/b3d5f7a9c1e2_add_currency_ledger.py"]
scope = ["src/hullbreach_server/db/models/ledger.py", "src/hullbreach_server/services/currency.py", "src/hullbreach_server/services/matches.py", "tests/unit/test_currency.py", "src/hullbreach_server/db/models/__init__.py", "src/hullbreach_server/auth/schemas.py", "src/hullbreach_server/api/me.py", "src/hullbreach_server/api/auth.py", "src/hullbreach_server/services/profile.py", "tests/unit/test_me.py", "docs/index.md", "src/hullbreach_server/db/migrations/versions/b3d5f7a9c1e2_add_currency_ledger.py"]

[[acceptance]]
text = "given a recorded match, when it is saved, then both players' balances increase by the documented amounts"
bound = false

[[acceptance]]
text = "given a profile, when the balance shows, then it equals recorded earnings minus purchases"
bound = false
+++

As a player, I want to earn in-game currency for completing matches, more for winning, so that playing is how I unlock cosmetics.

Open questions:
- Payout per match, per win, per first win of the day? Any cap to discourage farming?
- Do LAN matches pay out?
