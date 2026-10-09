+++
id = "01M2H5T11BBT0FQHR5JDXDKE4Q"
title = "S15 Navigate the site consistently"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T11ARH7FQCAQZ52ER1Y6"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0043"]
labels = ["jira:SCRUM-36", "owner:a-carten", "milestone:0.1.0"]
scope = ["web/src/App.tsx", "web/src/components/Footer.tsx", "web/src/components/Header.tsx", "web/src/router.tsx", "web/tests/unit/Header.test.tsx"]

[[acceptance]]
text = "given any page, when signed out, then the header shows login and register; when signed in, then username, profile, store, and logout"
bound = false

[[acceptance]]
text = "given the keyboard alone, when navigating, then every link and control is reachable"
bound = false
+++

As a player, I want the same header and footer on every page with login state, profile, and store links, so that I always know where I am and how to get anywhere else.

Open questions:
- Client-side routing library, or plain links between pages?
- Dark/light toggle, or is the dark cockpit theme the only theme?
