+++
id = "01M2H5T117A35Q8AA9THRZTTYB"
title = "S12 Equip a skin"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T10XRAQYXM52JKK4FTSQ"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-10-26T11:42:28Z"
aliases = ["T-0039"]
labels = ["needs-game", "milestone:0.3.0", "creates:src/hullbreach_server/services/equip.py", "creates:src/hullbreach_server/db/migrations/versions/c8d0e2f4a6b8_create_equipped_skins_table.py", "creates:changelog.d/*.added.md"]
scope = ["src/hullbreach_server/api/me.py", "src/hullbreach_server/db/models/inventory.py", "tests/unit/test_active_skin.py", "web/src/components/SkinPicker.tsx", "web/src/pages/Profile.tsx", "web/tests/unit/SkinPicker.test.tsx", "src/hullbreach_server/db/models/__init__.py", "src/hullbreach_server/services/profile.py", "src/hullbreach_server/services/account_deletion.py", "src/hullbreach_server/services/matchmaking.py", "src/hullbreach_server/api/matchmaking.py", "docs/index.md", "web/src/api/me.ts", "web/tests/fixtures/me.ts", "web/tests/unit/Profile.test.tsx", "src/hullbreach_server/services/equip.py", "src/hullbreach_server/db/migrations/versions/c8d0e2f4a6b8_create_equipped_skins_table.py", "changelog.d/*.added.md"]

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
