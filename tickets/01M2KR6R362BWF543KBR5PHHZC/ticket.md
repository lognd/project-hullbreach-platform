+++
id = "01M2KR6R362BWF543KBR5PHHZC"
title = "Add a request timeout to web/src/api/auth.ts's fetch calls"
type = "task"
category = "todo"
priority = "medium"
reporter = "human"
created = "2026-09-16T00:00:00Z"
updated = "2026-09-16T00:00:00Z"
aliases = ["T-0102"]
labels = ["jira:none"]
scope = ["web/src/api/auth.ts"]
+++

T-0017 implemented register()/login()/logout()/fetchSession() in web/src/api/auth.ts without a request timeout (e.g. AbortController-based); design/hullbreach.strata's REL200:f_register/f_login_web/f_logout waivers were written expecting T-0017 to declare/prove one. Add a real timeout (AbortSignal.timeout or equivalent) to every fetch call in this file and update/remove the corresponding REL200 waivers on the browser node.
