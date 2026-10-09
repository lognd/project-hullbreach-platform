+++
id = "01M4GR0H05370MAS4FBEQHMGJY"
title = "AppConfig.from_external silently misconfigures: cwd-relative pyproject, ignored unknown keys, unstripped CORS list"
type = "bug"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:16Z"
updated = "2026-10-09T16:30:16Z"
labels = ["origin:auditor"]
scope = ["src/hullbreach_server/app/config.py"]

[[acceptance]]
text = "Tests for typo key, off-cwd load, whitespace CORS list"
bound = false
+++

src/hullbreach_server/app/config.py:104,108,115,123. Misuse cases that give wrong results without error: (1) line 104 defaults to Path('pyproject.toml') relative to cwd, so db.get_engine and migrations/env.py run from any other directory silently drop file config and fall back to the default database_url (localhost, hullbreach:hullbreach creds, line 94). (2) AppConfig has no extra='forbid', so a typo such as [tool.hullbreach_server] databse_url is silently ignored. (3) line 115 splits HULLBREACH_CORS_ORIGINS on ',' without strip or empty filtering: 'a, b' yields ' b' and '' yields [''] which never match an Origin. Fix direction: model_config extra='forbid' (and surface unknown file keys), locate the config file explicitly (search upward or require HULLBREACH_CONFIG) and log which file/none was used at INFO, strip and drop empty CORS entries.
