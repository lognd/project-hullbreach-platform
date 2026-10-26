"""Unit tests for the operator console: redaction, transcript, y/N prompts."""

from __future__ import annotations

import io

from hullbreach_ops.console import REDACTED, Console, redact


def test_redact_hides_registered_and_pattern_secrets() -> None:
    # frob:tests src/hullbreach_ops/console.py::redact kind="unit"
    text = (
        "postgresql://hullbreach:hunter22@localhost:5432/db "
        "Authorization: Bearer abc.def-123 x-server-key: k3y-value "
        "my-registered-secret password=pw123"
    )
    shown = redact(text, ["my-registered-secret", "abc"])
    assert "hunter22" not in shown
    assert "abc.def-123" not in shown
    assert "k3y-value" not in shown
    assert "my-registered-secret" not in shown
    assert f"://hullbreach:{REDACTED}@localhost" in shown
    # Short "secrets" would shred ordinary text, so they are ignored.
    assert redact("abc", ["abc"]) == "abc"
    # password=... is only hidden in log mode (instructions name settings freely).
    assert "password=pw123" in shown
    assert "pw123" not in redact(text, log=True)


def test_console_writes_redacted_lines_and_keeps_a_transcript() -> None:
    # frob:tests src/hullbreach_ops/console.py::Console kind="unit"
    stream = io.StringIO()
    console = Console(stream, interactive=False)
    console.add_secret("s3cret-value")
    console.add_secret(None)
    console.line("the key is s3cret-value")
    console.status("PASS", "docker", "Docker is installed")
    console.steps(["first", "second"], "  ")
    console.secret_once("Key: ", "brand-new-key")
    shown = stream.getvalue()
    assert "s3cret-value" not in shown
    assert f"the key is {REDACTED}" in shown
    assert "[PASS]    docker           Docker is installed" in shown
    assert "  1. first\n  2. second\n" in shown
    # A new secret is shown once on screen but never kept in the transcript.
    assert "Key: brand-new-key" in shown
    assert "brand-new-key" not in console.transcript
    assert f"Key: {REDACTED}" in console.transcript
    assert console.muted().redact("s3cret-value") == REDACTED


def test_confirm_defaults_to_no() -> None:
    # frob:tests src/hullbreach_ops/console.py::Console kind="unit"
    quiet = Console(io.StringIO(), interactive=False)
    assert quiet.confirm("Install it?") is False
    assert "no terminal to ask; answering No" in quiet.transcript
    assert quiet.ask_text("Name: ") == ""
    assert quiet.ask_password("Password: ") == ""

    answers = iter(["", "n", "yes", "Y"])
    asking = Console(io.StringIO(), interactive=True, ask=lambda _q: next(answers))
    assert [asking.confirm("Go?") for _ in range(4)] == [False, False, True, True]

    def closed(_q: str) -> str:
        raise EOFError

    assert Console(io.StringIO(), interactive=True, ask=closed).confirm("Go?") is False

    secret = Console(io.StringIO(), interactive=True, ask_secret=lambda _q: "pw-typed")
    assert secret.ask_password("Password: ") == "pw-typed"
    assert "pw-typed" not in secret.transcript
    assert secret.redact("pw-typed") == "pw-typed"  # the caller decides
    secret.add_secret("pw-typed")
    assert secret.redact("pw-typed") == REDACTED
