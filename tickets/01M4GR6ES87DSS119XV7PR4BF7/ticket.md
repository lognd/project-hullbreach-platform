+++
id = "01M4GR6ES87DSS119XV7PR4BF7"
title = "Session token persisted in localStorage is readable by any XSS"
type = "security"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:33:30Z"
updated = "2026-10-09T16:51:17Z"
labels = ["origin:auditor", "creates:changelog.d/01M4GR6ES87DSS119XV7PR4BF7.changed.md"]
scope = ["web/src/auth/session.ts", "web/tests/setup.ts", "web/tests/unit/Login.test.tsx", "docs/index.md", "docs/design/sprint-1.md", "changelog.d/01M4GR6ES87DSS119XV7PR4BF7.changed.md"]

[[acceptance]]
text = "given a signed-in session, when localStorage and sessionStorage are inspected, then no token is present"
bound = false
+++

origin: auditor. Invariant INV-006 (policy rule: none expressible; see invariants/INV-006.md). web/src/auth/session.ts:32-53 stores the bearer token (14-day TTL) in window.localStorage. Any script injection exfiltrates a long-lived credential. Fix direction (needs a design decision, docs/design/sprint-1.md sec.6): keep the token in memory plus an HttpOnly SameSite cookie issued by the API, or at minimum shorten TTL and add rotation; if the cookie route is chosen revisit CORS (INV-004) and CSRF.
