+++
id = "01M5XX217WGTRZ8XE24BMEPR9H"
title = "Demo-only grant-credits command for the presenter"
type = "story"
category = "todo"
priority = "high"
reporter = "a-carten"
created = "2026-10-27T05:24:18Z"
updated = "2026-10-27T05:38:42Z"
scope = ["src/hullbreach_server/services/currency.py", "src/hullbreach_ops/**", "tests/unit/**", "docs/**", "Makefile", "changelog.d/**"]

[[acceptance]]
text = "given demo mode on and a real user, when grant-credits runs, then a demo_grant ledger row and a console DB line appear"
bound = true

[[acceptance]]
text = "given demo mode off, an unknown user or a non-positive amount, then the command refuses and writes nothing"
bound = true
+++
