+++
id = "01M4GREZ98HHCGREZDAV50P336"
title = "Cosmetic loadout model and migration (per-block-type skins plus trail, banner and projectile-effect slots)"
type = "task"
category = "todo"
priority = "medium"
points = 2
parent = "01M2H5T117A35Q8AA9THRZTTYB"
reporter = "lognd"
created = "2026-10-09T16:38:09Z"
updated = "2026-10-09T16:38:09Z"
labels = ["owner:lognd", "needs-game", "milestone:0.3.0"]

[[links]]
kind = "blocked-by"
target = "01M2H5T1227K1HMGED2B5K9JYQ"

[[acceptance]]
text = "A loadout row per user stores block type -> skin item id and one id per other category, each a foreign key to an owned inventory item."
bound = false

[[acceptance]]
text = "The database rejects a skin whose target block type differs from its slot, and an item in the wrong category slot."
bound = false

[[acceptance]]
text = "Retiring or losing an item resets its slot to the default."
bound = false
+++
