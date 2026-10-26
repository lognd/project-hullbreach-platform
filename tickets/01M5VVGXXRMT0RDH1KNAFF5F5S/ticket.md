+++
id = "01M5VVGXXRMT0RDH1KNAFF5F5S"
title = "Widen CORS allowed methods to PUT, PATCH, DELETE"
type = "bug"
category = "done"
outcome = "fixed"
priority = "medium"
reporter = "a-carten"
created = "2026-10-26T10:19:00Z"
updated = "2026-10-26T10:19:51Z"
scope = ["src/hullbreach_server/app/app.py", "tests/unit/test_app.py", "docs/index.md", "invariants/INV-004.md", "changelog.d/*"]

[[acceptance]]
text = "given a CORS preflight for PUT, PATCH or DELETE from an allowed origin, then the server allows it"
bound = true
+++
