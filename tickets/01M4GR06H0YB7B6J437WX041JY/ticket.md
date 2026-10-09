+++
id = "01M4GR06H0YB7B6J437WX041JY"
title = "SimpleFormatter drops exc_info/stack_info so logged exceptions lose tracebacks"
type = "bug"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:05Z"
updated = "2026-10-09T16:52:35Z"
labels = ["origin:auditor", "audit:logging"]
scope = ["src/hullbreach_server/logging/formatter.py"]

[[acceptance]]
text = "given an exception logged with log.exception, when SimpleFormatter formats it, then the traceback is appended"
bound = true
+++

formatter.py:15-20 SimpleFormatter.format returns only record.getMessage(); it never appends record.exc_text / formatter.formatException(record.exc_info) / formatStack. Contract of logging.Formatter.format (and of log.exception / exc_info=True) is violated: any caller using exception logging silently loses the traceback on both handlers. Fix: after building the line, if record.exc_info append self.formatException(record.exc_info) (cache in record.exc_text) and stack_info via formatStack; add a unit test using log.exception.
