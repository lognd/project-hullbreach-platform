+++
id = "01M4GR0D0R069EZKD3CT4GKWQR"
title = "api routes return undeclared JSONResponse errors: OpenAPI contract omits 401/409/429/503 and login logs raw username"
type = "bug"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:12Z"
updated = "2026-10-09T17:02:12Z"
labels = ["origin:auditor", "interface-audit"]
scope = ["src/hullbreach_server/api/auth.py", "src/hullbreach_server/api/health.py"]

[[acceptance]]
text = "given the OpenAPI schema, when read, then register/login/logout/session/ready list their error responses"
bound = false
+++

api/auth.py:86,117,156,176 and api/health.py:225 declare only the success response_model, yet register returns 409 {detail,field} (:94), login 401/429 (:127,:138), logout/session 401 via get_current_user, ready 503 {status,database} (:238). The generated /api/openapi.json (served by app/app.py:22) therefore does not describe the failure contract that the web client and game server (GET /auth/session) consume. Fix: add responses={409: ..., 401: ..., 429: ...} with pydantic models (e.g. ConflictResponse, ErrorDetail, NotReadyResponse) on each decorator. Also api/auth.py:137 logs payload.username verbatim at WARNING (unsanitized client input, log-injection/PII); log a length-capped repr or the user id. Also api/health.py:199 HealthResponse lacks the one-line docstring required for public symbols, and api/auth.py:158 parameter 'all' shadows the builtin (use Query(alias='all') with all_sessions).
