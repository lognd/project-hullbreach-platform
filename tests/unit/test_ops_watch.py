"""Unit tests for `console`: the live, readable view of the API log."""

from __future__ import annotations

from pathlib import Path

import pytest

from hullbreach_ops import lifecycle, watch
from tests.unit.ops_fakes import make_ctx, output

ACCESS_OK = (
    "[access] 2026-10-26T12:00:03Z POST /api/v1/auth/login 200 41.7ms user=u-1 key=no"
)
ACCESS_KEY = (
    "[access] 2026-10-26T12:00:05Z POST /api/v1/matches 201 12.0ms user=- key=yes"
)
ACCESS_BAD = "[access] 2026-10-26T12:00:06Z GET /api/v1/me 401 1.2ms user=- key=no"
EVENT = "[event] 2026-10-26T12:00:05Z match recorded: m-1, winner=ann, ratings ann 1200 -> 1216"
NOISE = "INFO     some uvicorn chatter that is not ours"
WARN = "WARNING: login failed: 'ann' (wrong password)"


def _write_log(tmp_path: Path, *lines: str):
    ctx = make_ctx(tmp_path)
    path = lifecycle.log_path(ctx, "api")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ctx


def test_watch_without_a_log_explains_how_to_start_the_stack(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/watch.py::watch kind="unit"
    ctx = make_ctx(tmp_path)

    result = watch.watch(ctx, show_events=False, lines=10, follow=False)

    assert result.is_err
    assert "make demo" in " ".join(result.danger_err.fix)


def test_watch_renders_access_lines_and_hides_events_by_default(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/watch.py::watch kind="unit"
    ctx = _write_log(tmp_path, NOISE, ACCESS_OK, EVENT, ACCESS_KEY, WARN)

    assert watch.watch(ctx, show_events=False, lines=10, follow=False).is_ok

    text = output(ctx)
    assert "12:00:03  POST   /api/v1/auth/login" in text
    assert "200" in text and "42ms" in text and "user=u-1" in text
    assert "[server-key]" in text
    assert "WARNING: login failed" in text
    assert "match recorded" not in text
    assert "chatter" not in text


def test_watch_db_mode_adds_event_lines(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/watch.py::watch kind="unit"
    ctx = _write_log(tmp_path, ACCESS_KEY, EVENT)

    assert watch.watch(ctx, show_events=True, lines=10, follow=False).is_ok

    assert "12:00:05  DB      match recorded: m-1, winner=ann" in output(ctx)


def test_watch_starts_with_only_the_last_n_lines(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/watch.py::watch kind="unit"
    ctx = _write_log(tmp_path, ACCESS_OK, ACCESS_KEY, ACCESS_BAD)

    assert watch.watch(ctx, show_events=False, lines=2, follow=False).is_ok

    text = output(ctx)
    assert "auth/login" not in text
    assert "api/v1/matches" in text and "api/v1/me" in text


def test_watch_never_prints_a_registered_secret(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/watch.py::watch kind="unit"
    ctx = _write_log(tmp_path, ACCESS_OK.replace("auth/login", "leak-s3cret-path"))
    ctx.console.add_secret("leak-s3cret-path")

    assert watch.watch(ctx, show_events=False, lines=10, follow=False).is_ok

    assert "leak-s3cret-path" not in output(ctx)


def test_watch_follows_new_lines_until_interrupted(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/watch.py::watch kind="unit"
    ctx = _write_log(tmp_path, ACCESS_OK)
    path = lifecycle.log_path(ctx, "api")
    ticks: list[float] = []

    def sleep(seconds: float) -> None:
        ticks.append(seconds)
        if len(ticks) == 1:
            with path.open("a", encoding="utf-8") as log:
                log.write(ACCESS_BAD + "\n")
        else:
            raise KeyboardInterrupt

    ctx.sleep = sleep

    assert watch.watch(ctx, show_events=False, lines=10, follow=True).is_ok

    text = output(ctx)
    assert text.index("auth/login") < text.index("api/v1/me")
    assert "Console stopped." in text


def test_watch_survives_the_log_being_reset(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/watch.py::watch kind="unit"
    ctx = _write_log(tmp_path, ACCESS_OK, ACCESS_KEY)
    path = lifecycle.log_path(ctx, "api")
    ticks: list[float] = []

    def sleep(seconds: float) -> None:
        ticks.append(seconds)
        if len(ticks) == 1:
            path.write_text(ACCESS_BAD + "\n", encoding="utf-8")
        elif len(ticks) > 3:
            raise KeyboardInterrupt

    ctx.sleep = sleep

    assert watch.watch(ctx, show_events=False, lines=0, follow=True).is_ok

    assert "api/v1/me" in output(ctx)


@pytest.mark.parametrize("status,code", [(200, "32"), (404, "33"), (503, "31")])
def test_status_is_coloured_by_class(status: int, code: str) -> None:
    # frob:tests src/hullbreach_ops/watch.py::_status_color kind="unit"
    assert watch._status_color(status) == code


ACCESS_BODY = (
    "[access] 2026-10-26T12:00:07Z POST /api/v1/store/purchase 200 9.0ms user=u-1 key=no "
    'name=demo_pilot body={"item_id":"rookie-stripes","password":"<redacted>"}'
)


def test_watch_shows_username_and_payload_summary(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/watch.py::watch kind="unit"
    ctx = _write_log(tmp_path, ACCESS_BODY)

    assert watch.watch(ctx, show_events=False, lines=10, follow=False).is_ok

    text = output(ctx)
    assert "user=demo_pilot" in text
    assert 'body={"item_id":"rookie-stripes","password":"<redacted>"}' in text


def test_watch_can_hide_payloads(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/watch.py::watch kind="unit"
    ctx = _write_log(tmp_path, ACCESS_BODY)

    result = watch.watch(
        ctx, show_events=False, lines=10, follow=False, show_payloads=False
    )

    assert result.is_ok
    assert "rookie-stripes" not in output(ctx)
    assert "user=demo_pilot" in output(ctx)


def test_watch_payload_view_still_masks_registered_secrets(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/watch.py::watch kind="unit"
    ctx = _write_log(tmp_path, ACCESS_BODY.replace("rookie-stripes", "leak-s3cret"))
    ctx.console.add_secret("leak-s3cret")

    assert watch.watch(ctx, show_events=False, lines=10, follow=False).is_ok

    assert "leak-s3cret" not in output(ctx)
