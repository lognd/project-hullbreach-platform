+++
id = "01M2KR6R31Z48GCVFTJFCXKB89"
title = "Widen strata tests node glob to cover web/tests"
type = "docs"
category = "done"
outcome = "done"
priority = "medium"
reporter = "human"
created = "2026-09-16T00:00:00Z"
updated = "2026-09-16T00:00:03Z"
aliases = ["T-0097"]
labels = ["jira:none"]
scope = ["design/hullbreach.strata", "docs/design/registry/capability-via-ratchet.lock.json", "docs/design/sprint-1.md"]

[[acceptance]]
text = "given design/hullbreach.strata's tests node, when frob check runs against a branch carrying web/tests/unit/Header.test.tsx and Login.test.tsx, then their observed client_storage capability is bound by the node's code glob (no SELFAUDIT001/SYS103 finding)"
bound = true
+++

found while working T-0096: the design's 'tests' node (design/hullbreach.strata) only globs 'tests/**', so web/tests/unit/*.test.tsx's observed client_storage capability (localStorage use in Header.test.tsx and Login.test.tsx) is unbound, tripping SELFAUDIT001/SYS103. Widen the node's code= glob (or add a second node) to also cover web/tests/**.

## Reopen log
- 2026-09-16: COV003: cmd: evidence is not allowed for kind=bug; replace with real pytest/vitest node-id evidence per CI's frob check finding
- 2026-09-16: web/scripts/run-vitest-ids.mjs (a node script) trips eslint's browser-only no-undef on process/console; needs an eslint.config.js override
