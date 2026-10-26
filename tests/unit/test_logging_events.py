"""Unit tests for the structured access and event log lines the demo console reads."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from hullbreach_server.logging import events
from hullbreach_server.logging.events import AccessEntry, EventEntry

_WHEN = datetime(2026, 10, 26, 12, 0, 3, tzinfo=UTC)


def test_access_line_round_trips_through_parse_line() -> None:
    # frob:tests src/hullbreach_server/logging/events.py::format_access kind="unit"
    # frob:tests src/hullbreach_server/logging/events.py::parse_line kind="unit"
    line = events.format_access(
        _WHEN, "POST", "/api/v1/matches", 201, 12.34, user_id="u-1", server_key=True
    )

    assert line.startswith("[access] 2026-10-26T12:00:03Z POST /api/v1/matches 201 ")
    entry = events.parse_line(line).danger_ok
    assert entry == AccessEntry(
        time=_WHEN,
        method="POST",
        path="/api/v1/matches",
        status=201,
        ms=12.3,
        user="u-1",
        server_key=True,
    )


def test_access_line_without_user_shows_a_dash_and_no_server_key() -> None:
    # frob:tests src/hullbreach_server/logging/events.py::format_access kind="unit"
    line = events.format_access(_WHEN, "GET", "/x", 401, 1.0, user_id=None)

    assert line.endswith("user=- key=no")
    entry = events.parse_line(line).danger_ok
    assert isinstance(entry, AccessEntry)
    assert (entry.user, entry.server_key) == ("-", False)


def test_access_line_cannot_be_forged_through_the_path() -> None:
    # frob:tests src/hullbreach_server/logging/events.py::format_access kind="unit"
    line = events.format_access(
        _WHEN, "GET", "/a b\n[event] 2026 fake", 404, 1.0, user_id=None
    )

    assert "\n" not in line
    assert " fake" not in line.split("GET ", 1)[1].split(" 404")[0]
    assert isinstance(events.parse_line(line).danger_ok, AccessEntry)


def test_log_event_emits_one_tagged_line_that_parses(
    caplog,
) -> None:
    # frob:tests src/hullbreach_server/logging/events.py::log_event kind="unit"
    log = logging.getLogger("hullbreach_server.test_events")
    with caplog.at_level(logging.INFO, logger=log.name):
        events.log_event(log, "user registered: %s", "ann")

    (record,) = [r for r in caplog.records if r.name == log.name]
    assert record.levelno == logging.INFO
    entry = events.parse_line(record.getMessage()).danger_ok
    assert isinstance(entry, EventEntry)
    assert entry.text == "user registered: ann"


def test_event_text_is_flattened_to_one_line() -> None:
    # frob:tests src/hullbreach_server/logging/events.py::format_event kind="unit"
    line = events.format_event(_WHEN, "a\nb\r\nc")

    assert line == "[event] 2026-10-26T12:00:03Z a b c"


def test_parse_line_rejects_untagged_and_malformed_lines() -> None:
    # frob:tests src/hullbreach_server/logging/events.py::parse_line kind="unit"
    for line in (
        "INFO:     Started server process [1]",
        "",
        "[access] not enough fields",
        "[access] 2026-10-26T12:00:03Z GET /x abc 1.0ms user=- key=no",
        "[event] yesterday something",
    ):
        assert events.parse_line(line).is_err
