+++
id = "01M2H5T102HP1A95G3TMYP9313"
title = "CI: restore coverage lock after refresh so main pushes stay clean"
type = "bug"
category = "done"
outcome = "done"
priority = "high"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:02Z"
aliases = ["T-0002"]
labels = ["jira:none"]
scope = [".github/workflows/ci.yml", "src/hullbreach_server/api/health.py", "src/hullbreach_server/logging/filter.py", "src/hullbreach_server/logging/formatter.py"]

[[acceptance]]
text = "given a push to main, when the frob check job runs, then PRE001/SCOPE001 do not fire"
bound = false
+++
