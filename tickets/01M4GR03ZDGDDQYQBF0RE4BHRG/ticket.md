+++
id = "01M4GR03ZDGDDQYQBF0RE4BHRG"
title = "verify_password raises on a malformed stored hash instead of honoring its bool contract"
type = "bug"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:03Z"
updated = "2026-10-09T17:00:59Z"
scope = ["src/hullbreach_server/auth/passwords.py"]

[[acceptance]]
text = "given a malformed stored hash, when verify_password runs, then it returns False without raising"
bound = true
+++

origin: auditor. auth/passwords.py:131-133 -- docstring and signature promise bool, but pwdlib's verify raises (e.g. UnknownHashError) when hashed is not a recognised hash (corrupt row, legacy/seeded value). Caller api/auth.py:112 does not catch it, so login returns 500 and leaks via error. Failure mode is undocumented. Fix: return Result[bool, PasswordError] (ErrorSet with MalformedHash) per typani convention, or catch and log then return False; document it and test with hashed='not-a-hash'. Callers (api/auth.py login) map Err to the same 401.
