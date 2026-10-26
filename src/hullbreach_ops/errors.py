"""The one error shape operator tooling returns: a message plus fix steps."""

from __future__ import annotations

from pydantic import BaseModel


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_start_reports_a_compose_failure_with_fix_steps
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class OpsError(BaseModel):
    """A failed operator step: what went wrong and the numbered steps that fix it.

    Messages never carry secret values (passwords, keys, database URLs).
    """

    message: str
    fix: list[str] = []

    def __str__(self) -> str:
        """The plain message, so f-strings and logs show it."""
        return self.message
