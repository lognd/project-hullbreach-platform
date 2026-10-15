+++
id = "01M505P94DYBTQJN62Y99XSJ66"
title = "Doctor: hullbreach_server doctor with demo profiles, support bundle and bootstrap wrappers"
type = "task"
category = "in-progress"
priority = "high"
points = 8
parent = "01M505NY7ZY9Y8HYFF8GGTC0R6"
reporter = "lognd"
created = "2026-10-15T16:17:57Z"
updated = "2026-10-15T17:28:15Z"
labels = ["owner:lognd", "milestone:0.2.0", "creates:src/hullbreach_ops/**", "creates:tests/unit/test_ops_*.py", "creates:doctor.sh", "creates:doctor.cmd", "creates:doctor.ps1", "creates:.nvmrc"]
scope = ["src/hullbreach_server/__main__.py", "README.md", "docs/**", "package.json", "frob.toml", "design/hullbreach.strata", "changelog.d/**", "src/hullbreach_ops/**", "tests/unit/test_ops_*.py", "doctor.sh", "doctor.cmd", "doctor.ps1", ".nvmrc", ".gitattributes", "invariants/INV-007.md", "tests/unit/ops_fakes.py", "tests/unit/test_main.py", "Makefile", ".env.example"]

[[acceptance]]
text = "given any machine, when ./doctor.sh runs, then missing git, uv, docker or node is explained in plain English and the official installer is offered only behind a y/N prompt"
bound = true

[[acceptance]]
text = "given a failing check, when the doctor reports, then it prints FAIL with numbered fix steps and a README link, and checks depending on it show PENDING"
bound = true

[[acceptance]]
text = "given doctor --demo website, guest, platform or online, when it finishes, then only the checks that demo needs ran and the exact next commands and game-side values are printed"
bound = true

[[acceptance]]
text = "given doctor --collect, when run, then a zip with the redacted doctor output and recent logs is written and no secret value appears in it"
bound = true

[[acceptance]]
text = "given a .env file, when the doctor runs, then it reports settings as set or unset and never prints their values"
bound = false
+++

Checks are a registry with ids and dependencies so README troubleshooting entries can cite check ids.
