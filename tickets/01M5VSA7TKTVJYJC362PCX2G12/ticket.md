+++
id = "01M5VSA7TKTVJYJC362PCX2G12"
title = "Replace REL200 timeout waivers in hullbreach.strata with a declared timeout"
type = "bug"
category = "todo"
priority = "medium"
reporter = "a-carten"
created = "2026-10-26T09:40:24Z"
updated = "2026-10-26T23:58:31Z"
scope = ["design/hullbreach.strata"]
+++

found while working ~R5PHHZC: web/src/api/auth.ts now times out every fetch via apiFetch (AbortController, 10 s), but the REL200 waivers for f_register/f_login_web/f_logout (ticket T-0102) remain because the strata syntax to declare a timeout is unknown. Convert them to a declared timeout and fix the stale 'persisted to localStorage' comment near line 27.
