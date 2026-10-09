from __future__ import annotations

import logging


# noqa: E501  # frob:tests tests/unit/test_logging.py::test_simple_formatter_prefixes_level_at_warning_and_above
# frob:doc docs/index.md#public-api
class SimpleFormatter(logging.Formatter):
    """Plain message for INFO/DEBUG; prefixes level name for WARNING and above.

    Tracebacks (`exc_info`) and `stack_info` are appended like the stdlib does.
    """

    def __init__(self, show_level: bool = False) -> None:
        super().__init__()
        self._show_level = show_level

    def format(self, record: logging.LogRecord) -> str:
        # frob:doc docs/index.md#public-api
        msg = record.getMessage()
        if self._show_level or record.levelno >= logging.WARNING:
            msg = f"{record.levelname}: {msg}"
        # Same tail as logging.Formatter.format: traceback (cached on the
        # record so sibling handlers format it once), then stack_info.
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            msg = f"{msg}\n{record.exc_text}"
        if record.stack_info:
            msg = f"{msg}\n{self.formatStack(record.stack_info)}"
        return msg
