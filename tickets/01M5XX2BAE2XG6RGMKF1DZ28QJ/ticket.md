+++
id = "01M5XX2BAE2XG6RGMKF1DZ28QJ"
title = "Seed richer demo match histories and add a match detail page"
type = "task"
category = "todo"
priority = "medium"
reporter = "a-carten"
created = "2026-10-27T05:24:28Z"
updated = "2026-10-27T05:24:28Z"
labels = ["creates:src/hullbreach_ops/demo_history.py"]
scope = ["src/hullbreach_ops/demo.py", "src/hullbreach_server/api/me.py", "src/hullbreach_server/services/matches.py", "tests/unit/test_ops_demo.py", "tests/unit/test_me_matches.py", "web/src/**", "web/tests/unit/**", "docs/**", "changelog.d/**", "README.md", "src/hullbreach_ops/demo_history.py"]

[[acceptance]]
text = "given make demo, when browsing matches, then several players have rows and each row opens a detail view"
bound = false
+++
