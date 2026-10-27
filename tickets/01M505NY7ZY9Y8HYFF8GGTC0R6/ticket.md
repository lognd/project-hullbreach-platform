+++
id = "01M505NY7ZY9Y8HYFF8GGTC0R6"
title = "Run and diagnose the platform locally with one doctor command"
type = "story"
category = "done"
outcome = "fixed"
priority = "high"
points = 13
parent = "01M2H5T104B4HY0X1B5KX80SJ7"
reporter = "lognd"
created = "2026-10-15T16:17:46Z"
updated = "2026-10-27T00:50:26Z"
persona = "first-time operator who has never used a terminal"
capability = "run one doctor command that checks every prerequisite and tells me exactly how to fix what is wrong, then start, stop and demo the platform with named scripts"
outcome_text = "I can demo the website and the guest, online and platform game modes without help"
labels = ["owner:lognd", "milestone:0.2.0", "creates:src/hullbreach_ops/**"]
scope = ["src/hullbreach_server/__main__.py", "README.md", "docs/**", "src/hullbreach_ops/**"]

[[acceptance]]
text = "given a fresh clone, when ./doctor.sh is run, then every check prints PASS, WARN or FAIL and each failure prints numbered fix steps and a README link"
bound = true

[[acceptance]]
text = "given a running stack, when make start, stop, status, reset-db, demo-users, server-key and lan are used, then each goes through one CLI implementation"
bound = true
+++

Umbrella story for the doctor and the run scripts. The doctor lives in the operator package hullbreach_ops so the API package keeps its no-subprocess policy (INV-007).
