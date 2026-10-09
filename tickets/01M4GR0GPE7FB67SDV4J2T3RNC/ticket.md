+++
id = "01M4GR0GPE7FB67SDV4J2T3RNC"
title = "AppConfig.from_external raises raw ValidationError/TOMLDecodeError instead of returning Result"
type = "bug"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:16Z"
updated = "2026-10-09T17:10:55Z"
labels = ["origin:auditor"]
scope = ["src/hullbreach_server/app/config.py"]

[[acceptance]]
text = "from_external returns Result; callers updated; tests for bad port, bad TOML"
bound = true
+++

src/hullbreach_server/app/config.py:98-123. from_external is fallible (HULLBREACH_PORT=abc, malformed pyproject.toml, wrong-typed [tool.hullbreach_server] values, unreadable file) but its signature and docs promise only AppConfig; failures escape as pydantic.ValidationError / tomllib.TOMLDecodeError / OSError tracebacks to __main__.main (__main__.py:189), db.get_engine, and migrations/env.py:35. Also the public docstring is a comment inside the body (line 101) not a docstring. Contract: return Result[AppConfig, ConfigError] with an ErrorSet covering unreadable file, TOML parse error, and validation error (message naming the offending key, never echoing database_url secrets); callers log and exit non-zero. Add a docstring stating the failure modes.
