+++
id = "01M2H5T127FEKMSVQSA2K2YHED"
title = "S22 Buy an item"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T1205GXC7WDK3G949GYJ"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0071"]
labels = ["jira:SCRUM-43", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/store.py", "src/hullbreach_server/services/store.py", "tests/unit/test_store_purchase.py", "web/src/components/ItemCard.tsx", "web/src/pages/Store.tsx", "web/tests/unit/Store.test.tsx"]

[[acceptance]]
text = "given enough currency, when buying an unowned item, then the balance decreases and the item is in the inventory immediately"
bound = false

[[acceptance]]
text = "given insufficient currency or an owned item, when buying, then refused with a clear reason and no balance change"
bound = false

[[acceptance]]
text = "given two rapid purchase requests for the same item, when processed, then exactly one purchase results"
bound = false
+++

As a player, I want to purchase an item with my currency, so that it appears in my inventory and can be equipped.

Open questions:
- Real-money payments are out of scope; confirm the store is currency-only.
- Refunds?
