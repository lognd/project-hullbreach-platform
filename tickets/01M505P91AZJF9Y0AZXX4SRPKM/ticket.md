+++
id = "01M505P91AZJF9Y0AZXX4SRPKM"
title = "Run scripts: start, stop, status, reset-db, demo-users, server-key and lan"
type = "task"
category = "in-progress"
priority = "high"
points = 5
parent = "01M505NY7ZY9Y8HYFF8GGTC0R6"
reporter = "lognd"
created = "2026-10-15T16:17:57Z"
updated = "2026-10-15T17:25:53Z"
labels = ["owner:lognd", "milestone:0.2.0", "creates:src/hullbreach_ops/**", "creates:tests/unit/test_ops_*.py"]
scope = ["src/hullbreach_server/__main__.py", "Makefile", "docker-compose.yml", "vite.config.ts", ".env.example", ".gitignore", "changelog.d/**", "src/hullbreach_ops/**", "tests/unit/test_ops_*.py", ".gitattributes", "package.json", "package-lock.json", ".nvmrc", "tests/unit/ops_fakes.py", "tests/unit/test_main.py", "tests/system/test_build.py"]

[[acceptance]]
text = "given configured ports, when hullbreach_server start runs, then the database is up and healthy, migrations and seed applied, API and web started in the background and their URLs printed"
bound = false

[[acceptance]]
text = "given a started stack, when stop and status run, then status reports each component and stop ends the processes it started"
bound = false

[[acceptance]]
text = "given reset-db, when the typed confirmation is not exactly the project name, then nothing is deleted"
bound = false

[[acceptance]]
text = "given server-key and demo-users, when run, then a strong key or two demo accounts are produced and secrets are never logged"
bound = false

[[acceptance]]
text = "given lan, when run, then API and web bind 0.0.0.0 and the LAN URL for a friend is printed"
bound = false
+++

One implementation in hullbreach_ops; Makefile targets are thin conveniences that call the CLI (T-3400: no frob-verb wrappers).
