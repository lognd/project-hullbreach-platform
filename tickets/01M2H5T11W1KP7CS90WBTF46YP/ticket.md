+++
id = "01M2H5T11W1KP7CS90WBTF46YP"
title = "Website match history page with paging"
type = "task"
category = "todo"
priority = "medium"
points = 3
parent = "01M2H5T11T3DJZ8N35J58RKTZ4"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-09T04:09:27Z"
aliases = ["T-0060"]
labels = ["jira:SCRUM-144", "owner:a-carten", "milestone:0.2.0"]
scope = ["web/src/pages/History.tsx", "web/tests/unit/History.test.tsx", "web/src/api/me.ts", "web/tests/fixtures/me.ts", "web/src/router.tsx", "web/src/components/MatchItem.tsx", "docs/index.md"]

[[acceptance]]
text = "given a page of matches, when load more is pressed, then the next page appends"
bound = false

[[acceptance]]
text = "Given a player with matches, when the history loads, then matches show newest first with opponent, result, date, duration, rating before and after and stats, and a Load more control while more remain"
bound = false

[[acceptance]]
text = "Given the last page, when it has loaded, then there is no Load more control"
bound = false

[[acceptance]]
text = "Given a failing load more, when it is pressed, then an error shows and the matches already loaded stay"
bound = false

[[acceptance]]
text = "Given a signed-out visitor, when the history renders, then it asks them to log in and makes no request"
bound = false
+++
