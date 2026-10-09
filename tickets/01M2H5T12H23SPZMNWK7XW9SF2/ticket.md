+++
id = "01M2H5T12H23SPZMNWK7XW9SF2"
title = "Admin void-match endpoint reversing rating and currency effects"
type = "task"
category = "todo"
priority = "medium"
points = 3
parent = "01M2H5T12F0VE61FR26RTG2NG3"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0081"]
labels = ["jira:SCRUM-196", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/admin/matches.py", "src/hullbreach_server/services/matches.py", "tests/unit/test_admin_void.py"]

[[acceptance]]
text = "given a voided match, when both players' balances and ratings are read, then they equal the pre-match values"
bound = false
+++
