from __future__ import annotations

import logging
import logging.config
import tomllib
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent / "config.toml"
_initialized = False


def _init() -> None:
    global _initialized
    if _initialized:
        return
    with _CONFIG_PATH.open("rb") as f:
        cfg = tomllib.load(f)
    logging.config.dictConfig(cfg)
    _initialized = True


# frob:tests tests/unit/test_logging.py::test_get_logger_returns_a_configured_logger
# frob:doc docs/index.md#public-api
def get_logger(name: str) -> logging.Logger:
    """Return a configured logger. Call with __name__ from each module."""
    _init()
    return logging.getLogger(name)
