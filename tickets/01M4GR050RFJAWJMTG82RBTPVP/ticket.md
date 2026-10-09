+++
id = "01M4GR050RFJAWJMTG82RBTPVP"
title = "Package __all__ omits symbols the api layer consumes (require_admin, schemas, rate-limit helpers); callers import submodules"
type = "bug"
category = "todo"
priority = "low"
reporter = "lognd"
created = "2026-10-09T16:30:04Z"
updated = "2026-10-09T17:00:38Z"
scope = ["src/hullbreach_server/auth/__init__.py"]

[[acceptance]]
text = "given the auth package, when api/auth.py imports, then every consumed symbol comes from hullbreach_server.auth"
bound = false
+++

origin: auditor. auth/__init__.py:15-25 -- documented public API (require_admin, RegisterRequest/LoginRequest/LoginResponse/UserProfile/SessionInfo, is_login_rate_limited, record_failed_login, clear_failed_logins, current_time) is absent from __all__, and api/auth.py:12-29 plus tests import from deps/sessions/schemas directly, so the real boundary is undefined and private-module moves break callers. Fix: re-export the consumed symbols from the package and switch callers to 'from hullbreach_server.auth import ...'; or document submodules as the public surface.
