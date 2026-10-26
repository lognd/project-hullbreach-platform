"""User-facing terminal output for the doctor and scripts.

This is deliberate CLI output, not logging: the operator reads it. Every
line passes through redaction (secret values registered with `add_secret`
and anything that looks like a credential) and is kept in a transcript so
`doctor --collect` can save exactly what was shown.
"""

from __future__ import annotations

import getpass
import io
import re
import sys
from collections.abc import Callable, Sequence
from typing import TextIO

from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

REDACTED = "<redacted>"

# Credentials that may appear in text we did not write ourselves (error
# messages, log tails): URL passwords, bearer tokens and server keys.
_PATTERNS = (
    (re.compile(r"(://[^:/@\s]+:)[^@\s]+(@)"), r"\1" + REDACTED + r"\2"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"), r"\1" + REDACTED),
    (
        re.compile(r"(?i)(x-server-key[\"']?\s*[:=]\s*[\"']?)[^\s\"',]+"),
        r"\1" + REDACTED,
    ),
)
# Extra patterns for log files only: any key=value whose key names a secret.
# Not applied to our own instructions, which mention setting names freely.
_LOG_PATTERNS = (
    (
        re.compile(
            r"(?i)((?:password|secret|token|api_keys?)[\"']?\s*[:=]\s*[\"']?)"
            r"[^\s\"',]+"
        ),
        r"\1" + REDACTED,
    ),
)
_ANSI = {"PASS": "32", "WARN": "33", "FAIL": "31", "PENDING": "36", "SKIP": "90"}


# noqa: E501  # frob:tests tests/unit/test_ops_console.py::test_redact_hides_registered_and_pattern_secrets
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def redact(text: str, secrets: Sequence[str] = (), *, log: bool = False) -> str:
    """Replace known secret values and credential-looking tokens in `text`.

    `log=True` also hides any `password=...`-style pair, for log files.
    """
    for secret in sorted((s for s in secrets if len(s) >= 4), key=len, reverse=True):
        text = text.replace(secret, REDACTED)
    for pattern, replacement in _PATTERNS + (_LOG_PATTERNS if log else ()):
        text = pattern.sub(replacement, text)
    return text


# noqa: E501  # frob:tests tests/unit/test_ops_console.py::test_console_writes_redacted_lines_and_keeps_a_transcript
# frob:tests tests/unit/test_ops_console.py::test_confirm_defaults_to_no
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class Console:
    """Prints operator output, asks y/N questions, and records a redacted transcript."""

    def __init__(
        self,
        stream: TextIO | None = None,
        *,
        interactive: bool | None = None,
        color: bool = False,
        ask: Callable[[str], str] = input,
        ask_secret: Callable[[str], str] = getpass.getpass,
    ) -> None:
        self._stream = stream if stream is not None else sys.stdout
        self._interactive = (
            interactive if interactive is not None else sys.stdin.isatty()
        )
        self._color = color
        self._ask = ask
        self._ask_secret = ask_secret
        self._secrets: list[str] = []
        self._transcript: list[str] = []

    def muted(self) -> Console:
        """A console that shares this one's secrets but shows nothing and never asks."""
        quiet = Console(io.StringIO(), interactive=False)
        quiet._secrets = self._secrets
        return quiet

    @property
    def interactive(self) -> bool:
        """True when a person can answer prompts."""
        return self._interactive

    @property
    def transcript(self) -> str:
        """Everything printed so far, redacted, without colour codes."""
        return "\n".join(self._transcript) + "\n"

    def add_secret(self, value: str | None) -> None:
        """Never print `value`: it is replaced by <redacted> wherever it appears."""
        if value and value not in self._secrets:
            self._secrets.append(value)

    def redact(self, text: str, *, log: bool = False) -> str:
        """`text` with every registered secret and credential pattern hidden."""
        return redact(text, self._secrets, log=log)

    def line(self, text: str = "") -> None:
        """Print one line (or several, if `text` has newlines)."""
        clean = self.redact(text)
        self._transcript.append(clean)
        self._stream.write(clean + "\n")
        self._stream.flush()

    def secret_once(self, label: str, value: str) -> None:
        """Print a new secret the operator must copy; never transcribed."""
        self._transcript.append(f"{label}{REDACTED}")
        self._stream.write(f"{label}{value}\n")
        self._stream.flush()

    def heading(self, text: str) -> None:
        """Print a section heading with a blank line before it."""
        self.line()
        self.line(text)
        self.line("-" * len(text))

    def status(self, status: str, label: str, summary: str) -> None:
        """Print one checklist row such as `[PASS] docker  Docker is installed`."""
        tag = f"[{status}]".ljust(10)
        plain = f"{tag}{label.ljust(16)} {summary}"
        clean = self.redact(plain)
        self._transcript.append(clean)
        if self._color and status in _ANSI:
            shown = clean.replace(tag, f"\x1b[{_ANSI[status]}m{tag}\x1b[0m", 1)
        else:
            shown = clean
        self._stream.write(shown + "\n")
        self._stream.flush()

    def steps(self, steps: Sequence[str], indent: str = "            ") -> None:
        """Print numbered steps, one per line."""
        for number, step in enumerate(steps, start=1):
            self.line(f"{indent}{number}. {step}")

    def confirm(self, question: str) -> bool:
        """Ask a y/N question; anything but y/yes (or no terminal) means No."""
        if not self._interactive:
            self.line(f"{question} [y/N] (no terminal to ask; answering No)")
            _log.info("confirm: non-interactive, answered no")
            return False
        try:
            answer = self._ask(f"{question} [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        self._transcript.append(f"{question} [y/N] {answer}")
        agreed = answer in ("y", "yes")
        _log.info("confirm: answered %s", "yes" if agreed else "no")
        return agreed

    def ask_text(self, question: str) -> str:
        """Ask for a line of text; "" when there is no terminal."""
        if not self._interactive:
            return ""
        try:
            answer = self._ask(question).strip()
        except EOFError:
            answer = ""
        self._transcript.append(f"{question}{answer}")
        return answer

    def ask_password(self, question: str) -> str:
        """Ask for a password without echoing it; "" when there is no terminal.

        The caller registers the answer with add_secret once it is accepted, so
        a rejected short answer (say "a") does not redact every "a" printed.
        """
        if not self._interactive:
            return ""
        try:
            answer = self._ask_secret(question)
        except EOFError:
            answer = ""
        self._transcript.append(f"{question}{REDACTED if answer else ''}")
        return answer
