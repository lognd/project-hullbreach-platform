+++
id = "01M4GR0HE6CC7F1SAG0TFY7HA7"
title = "create_app enables credentialed CORS with wildcard methods/headers and unvalidated cors_origins"
type = "security"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:16Z"
updated = "2026-10-09T17:11:00Z"
labels = ["origin:auditor"]
scope = ["src/hullbreach_server/app/app.py"]

[[acceptance]]
text = "given a wildcard origin, when config loads, then it is rejected; and preflights for other methods or headers are refused"
bound = false
+++

src/hullbreach_server/app/app.py:29-35 with config.py:95,115. allow_credentials=True, allow_methods=['*'], allow_headers=['*'] are hardcoded while allow_origins comes straight from HULLBREACH_CORS_ORIGINS. Setting it to '*' (or an attacker-influenced/overbroad value) makes Starlette reflect any Origin with credentials allowed, enabling cross-site credentialed requests. Contract: create_app must refuse or reject '*' (and non-http(s) origins) when credentials are allowed, and restrict methods/headers to those the API uses. Fix: validate cors_origins in AppConfig (field_validator) and narrow allow_methods/allow_headers; add a test that '*' is rejected.
