from __future__ import annotations

import logging
import logging.config
import threading
import tomllib
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent / "config.toml"
_initialized = False
_init_lock = threading.Lock()


def _init() -> None:
    """Load config.toml into logging.config.dictConfig exactly once, thread-safely."""
    global _initialized
    with _init_lock:
        if _initialized:
            return
        with _CONFIG_PATH.open("rb") as f:
            cfg = tomllib.load(f)
        logging.config.dictConfig(cfg)
        _initialized = True


# frob:tests tests/unit/test_logging.py::test_get_logger_returns_a_configured_logger
# frob:doc docs/index.md#public-api
def get_logger(name: str) -> logging.Logger:
    """Return a configured logger. Call with __name__ from each module.

    The first call loads logging/config.toml; a missing or invalid file raises
    (tomllib.TOMLDecodeError, OSError, ValueError) from every importing module
    at import time -- a broken logging setup is a programmer error, not a
    runtime condition to recover from.
    """
    _init()
    return logging.getLogger(name)


_LOG_VALUE_MAX = 64


# frob:invariant INV-003
# frob:doc docs/index.md#public-api
def sanitize_for_log(value: str, limit: int = _LOG_VALUE_MAX) -> str:
    """Return `value` as a length-capped repr, safe to log from unauthenticated input.

    repr() escapes CR/LF and other control characters (no forged log lines);
    the cap bounds log volume and how much of a mistyped secret lands in a log.
    """
    if len(value) > limit:
        return repr(value[:limit]) + f"...(+{len(value) - limit} chars)"
    return repr(value)
