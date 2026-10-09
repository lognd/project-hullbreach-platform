+++
id = "01M4GR071TMY19HWB9KDA5X5DF"
title = "BelowLevelFilter silently defaults unknown level name to WARNING"
type = "bug"
category = "done"
outcome = "fixed"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:06Z"
updated = "2026-10-09T16:52:57Z"
labels = ["origin:auditor", "audit:logging"]
scope = ["src/hullbreach_server/logging/filter.py"]

[[acceptance]]
text = "given an unknown level name, when BelowLevelFilter is built, then ValueError is raised"
bound = true
+++

filter.py:18 logging.getLevelNamesMapping().get(below.upper(), logging.WARNING) swallows a typo (e.g. below='WARN1NG' or 'warn') and silently uses WARNING; the constructor docstring states no failure behaviour. A misconfig in config.toml would mis-route records with no signal. Fix: raise ValueError for an unknown name (dictConfig surfaces it at startup) or accept int levels explicitly; document it in the docstring; add a test for the unknown-name case.
