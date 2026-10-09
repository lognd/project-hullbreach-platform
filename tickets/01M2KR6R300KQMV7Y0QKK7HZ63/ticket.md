+++
id = "01M2KR6R300KQMV7Y0QKK7HZ63"
title = "Sprint 1 failing test skeleton (web)"
type = "docs"
category = "done"
outcome = "done"
priority = "medium"
reporter = "human"
created = "2026-09-16T00:00:00Z"
updated = "2026-09-16T00:00:03Z"
aliases = ["T-0096"]
labels = ["jira:none"]
scope = ["web/tests/unit/Header.test.tsx", "web/tests/unit/Register.test.tsx", "web/tests/unit/Login.test.tsx", "package.json", "package-lock.json", "design/hullbreach.strata", "docs/design/registry/capability-via-ratchet.lock.json", "docs/design/sprint-1.md"]

[[acceptance]]
text = "given the sprint-1 web ticket bodies, when the failing-test skeleton is run, then vitest reports every planned it.fails node id passing (expected-fail) with no accidental xpass"
bound = true
+++

Test-first failing-test skeleton (vitest it.fails) for the sprint-1 web tickets T-0044, T-0017, T-0021, T-0024, per docs/design/sprint-1.md section 7. Adds @testing-library/user-event as a devDependency for keyboard/click interaction in the header tab-order test.

## Reopen log
- 2026-09-16: SELFAUDIT001/SYS100: now that Header.test.tsx and Login.test.tsx exist on this branch, the tests node's client_storage capability is observed but not declared -- add the may via grants T-0097 deferred
