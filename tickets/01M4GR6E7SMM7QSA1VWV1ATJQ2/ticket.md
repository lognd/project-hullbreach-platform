+++
id = "01M4GR6E7SMM7QSA1VWV1ATJQ2"
title = "Bound unauthenticated auth inputs: max_length on username, email, password"
type = "security"
category = "done"
outcome = "fixed"
priority = "high"
reporter = "lognd"
created = "2026-10-09T16:33:30Z"
updated = "2026-10-09T17:02:22Z"
labels = ["origin:auditor"]
scope = ["src/hullbreach_server/auth/schemas.py"]

[[acceptance]]
text = "given a password over 128 chars, when POST /register or /login, then 422 before any hashing"
bound = true

[[acceptance]]
text = "given a username over its cap, when POST /login, then 422 and nothing is stored in the failed-attempt dict"
bound = true
+++

origin: auditor. Invariant INV-002 (policy rule: none expressible, this frob has no pattern-rule engine; see invariants/INV-002.md). auth/schemas.py:33 RegisterRequest.password has min_length=8 only; LoginRequest (line 80) and username/email have no bounds. A multi-megabyte password is hashed by Argon2id on /register and verified on /login (CPU/memory DoS, pre-auth). Fix: Field(max_length=128) on password (login too), bounded username (e.g. 3..32 with a charset pattern) and email (<=254); add 422 tests for oversize values. Related: 01M4GR0CQQA02HKSTK8TDEV1SB covers the username cap for the failed-login store.
