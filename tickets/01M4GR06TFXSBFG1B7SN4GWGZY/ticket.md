+++
id = "01M4GR06TFXSBFG1B7SN4GWGZY"
title = "Login logs attacker-controlled username unescaped (log injection, mistyped-password leak)"
type = "security"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:06Z"
updated = "2026-10-09T17:01:52Z"
labels = ["origin:auditor", "audit:logging"]
scope = ["src/hullbreach_server/api/auth.py"]

[[acceptance]]
text = "given a username containing CR/LF, when login logs it, then exactly one escaped log record is produced"
bound = true
+++

api/auth.py:103 and :114 log payload.username with %s on warning paths (rate limited / invalid credentials). Username is unauthenticated input: embedded CR/LF forges log lines because SimpleFormatter (logging/formatter.py:17) does no neutralisation, and users who type a password into the username field get it written to stdout/stderr logs. Fix: log %r (escapes control chars) with a length cap, or log a short hash of the username; optionally have SimpleFormatter escape \r\n in the message. Add test asserting a username containing a newline yields a single log line.
