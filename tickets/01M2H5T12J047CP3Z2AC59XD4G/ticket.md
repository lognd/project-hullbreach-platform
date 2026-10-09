+++
id = "01M2H5T12J047CP3Z2AC59XD4G"
title = "S25 Curate the item catalog"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T12AMDB83JD0BVTR1BQP"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0082"]
labels = ["jira:SCRUM-46", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/admin/items.py", "src/hullbreach_server/services/catalog.py", "tests/unit/test_admin_items.py", "web/src/pages/admin/Items.tsx", "web/tests/unit/AdminItems.test.tsx"]

[[acceptance]]
text = "given an admin, when they create an item or change its name, price, category, or preview, or retire it, then it saves"
bound = false

[[acceptance]]
text = "given a retired item, when the store loads, then it is absent, but owners keep it"
bound = false

[[acceptance]]
text = "given a catalog change, when players reload, then they see it without a redeploy"
bound = false
+++

As a administrator, I want to add, edit, price, and retire catalog items, so that the store can change without a code deploy.

Open questions:
- Preview images: uploaded through the admin UI, or referenced by URL?
- Retiring an item: hide from the store but keep it for owners?
