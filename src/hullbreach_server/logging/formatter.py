from __future__ import annotations

import logging


# frob:tests tests/unit/test_logging.py::test_simple_formatter_prefixes_level_at_warning_and_above  # noqa: E501
# frob:waive WIRE001 reason="constructed by logging.config.dictConfig from the '()' factory string in config.toml, never by a Python call token" follow_up="T-0001"  # noqa: E501
# frob:doc docs/index.md#public-api
class SimpleFormatter(logging.Formatter):
    """Plain message for INFO/DEBUG; prefixes level name for WARNING and above."""

    def __init__(self, show_level: bool = False) -> None:
        super().__init__()
        self._show_level = show_level

    # frob:waive WIRE001 reason="called by the stdlib logging machinery on every record, never by a Python call token" follow_up="T-0001"  # noqa: E501
    def format(self, record: logging.LogRecord) -> str:
        # frob:doc docs/index.md#public-api
        msg = record.getMessage()
        if self._show_level or record.levelno >= logging.WARNING:
            return f"{record.levelname}: {msg}"
        return msg
