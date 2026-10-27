+++
id = "01M5XX28K491XN5RNGABW0Q5RP"
title = "Return per-field registration errors and show them inline"
type = "bug"
category = "todo"
priority = "high"
reporter = "a-carten"
created = "2026-10-27T05:24:25Z"
updated = "2026-10-27T05:41:11Z"
labels = ["creates:tests/unit/test_register_errors.py"]
scope = ["src/hullbreach_server/auth/**", "src/hullbreach_server/api/auth.py", "src/hullbreach_server/app/app.py", "tests/unit/test_auth_register.py", "web/src/api/auth.ts", "web/src/pages/Register.tsx", "web/tests/unit/Register.test.tsx", "docs/index.md", "changelog.d/**", "tests/unit/test_register_errors.py"]

[[acceptance]]
text = "given a weak or short password, when registering, then the API names the password field and the rule"
bound = true
+++
