+++
id = "01M4GR03P2MAC7ASRP2XGJV9R3"
title = "Failed-login store grows unbounded: entries for a username are never evicted unless that username logs in"
type = "security"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:02Z"
updated = "2026-10-09T16:30:02Z"
scope = ["src/hullbreach_server/auth/sessions.py"]
+++

origin: auditor. auth/sessions.py:166,194-231 -- _failed_attempts is a defaultdict(deque); _prune_stale_attempts empties a deque but never deletes the key, and is_login_rate_limited (line 222) creates a key for any probed name via defaultdict indexing. An attacker posting random usernames to /login grows memory without bound. Also the check (api/auth.py:102) and record (line 113) are separate lock acquisitions, so concurrent requests can exceed the max. Fix: delete the key when its deque is empty after pruning, use _failed_attempts.get in is_login_rate_limited, cap total keys, and consider a single atomic check_and_record function.
