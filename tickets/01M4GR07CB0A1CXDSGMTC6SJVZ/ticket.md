+++
id = "01M4GR07CB0A1CXDSGMTC6SJVZ"
title = "No integration test for logging config.toml routing; get_logger init contract undocumented"
type = "bug"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:06Z"
updated = "2026-10-09T16:52:59Z"
labels = ["origin:auditor", "audit:logging"]
scope = ["tests/unit/test_logging.py"]

[[acceptance]]
text = "given the shipped config.toml, when INFO and WARNING records are logged, then INFO goes to stdout only and WARNING+ to stderr once"
bound = false
+++

tests/unit/test_logging.py:28-31 test_get_logger_returns_a_configured_logger only asserts isinstance(Logger); nothing exercises logger.py::_init / config.toml with real handlers (INFO to stdout without prefix, WARNING+ only to stderr with 'LEVEL: ' prefix, no duplicate emission, idempotent second call). get_logger (logger.py:24-27) docstring also omits failure behaviour: a missing/invalid config.toml raises from tomllib/dictConfig at import time of every caller module (api, auth, db, app), and _init (logger.py:12-19) is not thread-safe (flag set after dictConfig). Fix: add a capsys/capfd test via get_logger + real caller (e.g. app or auth) asserting stream routing; document the raise in the docstring (or return Result per typani convention); guard _init with a lock.
