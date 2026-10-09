+++
id = "01M2Y1SM370GG28KN9CKEES0WW"
title = "Leave teammate breadcrumbs: pick-up guide and frob:todo markers at every plug-in point"
type = "docs"
category = "done"
outcome = "done"
priority = "high"
reporter = "human"
created = "2026-09-20T00:00:00Z"
updated = "2026-10-09T04:07:00Z"
aliases = ["T-0103"]
labels = ["jira:none"]
scope = ["docs/picking-up-work.md", "README.md", "CONTRIBUTING.md", "docs/index.md", "src/hullbreach_server/api/__init__.py", "src/hullbreach_server/db/models/__init__.py", "src/hullbreach_server/api/auth.py", "web/src/router.tsx", "web/src/App.tsx", "web/src/components/Footer.tsx", "web/src/api/auth.ts"]

[[acceptance]]
text = "given a new teammate, when they read docs/picking-up-work.md, then they can claim a queued ticket and know which file and example to start from"
bound = true

[[acceptance]]
text = "Given each code site a queued ticket plugs into, when a teammate opens the file, then a frob:todo marker names the owning ticket"
bound = true
+++

Sprint 1 landed as one author. The remaining backlog (T-0031 onward) is where teammates pick up. Leave a lane-by-lane pick-up guide and a frob:todo T-#### marker at each code site a queued ticket plugs into, so the next person landing in a file sees which ticket owns the gap.
