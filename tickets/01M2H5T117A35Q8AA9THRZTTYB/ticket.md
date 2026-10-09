+++
id = "01M2H5T117A35Q8AA9THRZTTYB"
title = "S12 Equip a skin"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T10XRAQYXM52JKK4FTSQ"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0039"]
labels = ["needs-game", "milestone:0.3.0"]
scope = ["src/hullbreach_server/api/me.py", "src/hullbreach_server/db/models/inventory.py", "tests/unit/test_active_skin.py", "web/src/components/SkinPicker.tsx", "web/src/pages/Profile.tsx", "web/tests/unit/SkinPicker.test.tsx"]

[[acceptance]]
text = "given owned skins, when one is selected as active, then it saves; given an unowned skin, then refused"
bound = false

[[acceptance]]
text = "given an active skin, when the next match starts, then both players see it on the ship"
bound = false
+++

As a player, I want to choose which owned skin my ship uses, so that my ship looks the way I want in every match.

Open questions:
- Per-ship, per-block-type, or one ship-wide palette?
- Chosen on the website only, in the game only, or both?
