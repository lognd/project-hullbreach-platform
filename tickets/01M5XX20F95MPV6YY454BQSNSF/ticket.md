+++
id = "01M5XX20F95MPV6YY454BQSNSF"
title = "Console shows authenticated username and sanitized request payload"
type = "story"
category = "todo"
priority = "high"
reporter = "a-carten"
created = "2026-10-27T05:24:17Z"
updated = "2026-10-27T05:38:38Z"
scope = ["src/hullbreach_server/app/**", "src/hullbreach_server/logging/**", "src/hullbreach_server/auth/deps.py", "src/hullbreach_ops/watch.py", "src/hullbreach_ops/cli.py", "src/hullbreach_ops/lifecycle.py", "tests/unit/**", "docs/**", "Makefile", "changelog.d/**"]

[[acceptance]]
text = "given a JSON request, when console-db runs, then the line shows method, path, status, duration, username and a sanitized payload summary"
bound = true

[[acceptance]]
text = "given passwords, tokens, secrets or hashes at any nesting depth, then the payload summary never contains them"
bound = false
+++
