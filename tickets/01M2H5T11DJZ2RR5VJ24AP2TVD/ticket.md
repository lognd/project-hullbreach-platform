+++
id = "01M2H5T11DJZ2RR5VJ24AP2TVD"
title = "S13 Learn what the game is from the landing page"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T11ARH7FQCAQZ52ER1Y6"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0045"]
labels = ["jira:SCRUM-34", "owner:a-carten", "milestone:0.3.0"]
scope = ["web/src/pages/Landing.tsx", "web/tests/unit/Landing.test.tsx"]

[[acceptance]]
text = "given the landing page, when it loads, then one screen explains the premise and links to register, log in, and download"
bound = false

[[acceptance]]
text = "given phone, tablet, and desktop widths, when rendered, then the layout is correct"
bound = false

[[acceptance]]
text = "given crunk check, when run on the page, then every color and spacing value comes from the design system"
bound = false
+++

As a visitor, I want a landing page that explains the game and shows how to get it, so that I can decide whether to make an account.

Open questions:
- Where does the download link point: GitHub release, itch.io, or a file on the platform host?
- Live stats (players online, matches today) on the landing page?
