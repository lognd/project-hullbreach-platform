+++
id = "01M4GR046X1E3PJ3GBPQ0YX7H3"
title = "Env-config readers raise bare ValueError at request time and accept nonsensical values"
type = "bug"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:03Z"
updated = "2026-10-09T17:01:12Z"
scope = ["src/hullbreach_server/auth/sessions.py"]

[[acceptance]]
text = "given a non-numeric or non-positive auth env var, when validate_auth_env runs, then Err names the variable and the readers fall back to defaults"
bound = true
+++

origin: auditor. auth/sessions.py:170-191 -- _session_ttl_seconds/_login_rate_limit_max/_login_rate_limit_window_seconds use int(raw) with no validation: a non-numeric env var raises ValueError inside issue_session or is_login_rate_limited (HTTP 500 on login), and 0/negative TTL issues already-expired sessions while max=0 locks every account out. Fix: parse and validate (positive int) once at startup via a pydantic settings model, failing fast with a clear message; or return Result from the readers.
