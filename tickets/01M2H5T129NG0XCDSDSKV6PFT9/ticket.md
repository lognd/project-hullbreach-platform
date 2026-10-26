+++
id = "01M2H5T129NG0XCDSDSKV6PFT9"
title = "Website buy button with confirmation and error states"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T127FEKMSVQSA2K2YHED"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-26T11:31:12Z"
aliases = ["T-0073"]
labels = ["jira:SCRUM-186", "owner:a-carten", "milestone:0.3.0", "creates:web/src/api/store.ts", "creates:web/tests/fixtures/store.ts"]
scope = ["web/src/components/ItemCard.tsx", "web/src/pages/Store.tsx", "web/tests/unit/Store.test.tsx", "docs/index.md", "web/src/api/store.ts", "web/tests/fixtures/store.ts"]

[[acceptance]]
text = "given insufficient currency, when buy is pressed, then the refusal reason shows and the balance is unchanged"
bound = false
+++
