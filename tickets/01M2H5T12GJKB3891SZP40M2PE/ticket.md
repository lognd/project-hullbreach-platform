+++
id = "01M2H5T12GJKB3891SZP40M2PE"
title = "Admin set-rating endpoint writing a RatingChange with the admin's reason"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T12F0VE61FR26RTG2NG3"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0080"]
labels = ["jira:SCRUM-195", "owner:lognd", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/admin/ratings.py", "src/hullbreach_server/services/admin.py", "tests/unit/test_admin_ratings.py"]

[[acceptance]]
text = "given a set-rating call, when applied, then history shows the admin entry and the new rating"
bound = false
+++
