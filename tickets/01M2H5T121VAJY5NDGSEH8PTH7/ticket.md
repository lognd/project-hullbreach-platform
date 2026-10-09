+++
id = "01M2H5T121VAJY5NDGSEH8PTH7"
title = "S20 Browse the catalog"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T1205GXC7WDK3G949GYJ"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-09T16:38:08Z"
aliases = ["T-0065"]
labels = ["jira:SCRUM-41", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/catalog.py", "src/hullbreach_server/db/migrations/", "src/hullbreach_server/db/models/inventory.py", "src/hullbreach_server/db/models/item.py", "src/hullbreach_server/services/catalog.py", "tests/unit/test_catalog.py", "tests/unit/test_item_models.py", "web/src/components/ItemCard.tsx", "web/src/pages/Store.tsx", "web/tests/unit/Store.test.tsx"]

[[acceptance]]
text = "given at least 100 items, when browsing by category, then name, preview, price, and owned flag show"
bound = false

[[acceptance]]
text = "given the website, when the catalog is served, then it comes from the database, not hard-coded"
bound = false
+++

As a player, I want to browse skins and other items with names, previews, and prices, so that I can decide what to spend my currency on.

Open questions:
- Categories: skins, block cosmetics, trails, banners? Which ship in v1?
- Previews: static images, or rendered from the same assets the game uses?
