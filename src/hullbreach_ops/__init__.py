"""Operator tooling: the doctor and the start/stop/demo scripts.

This package is separate from `hullbreach_server` on purpose. It is the
only code that spawns processes (docker, npm, git), and the API package
must never do that (INV-007, POL-no-subprocess). Request-handling code
never imports this package; only the CLI entry point does, lazily.
"""
