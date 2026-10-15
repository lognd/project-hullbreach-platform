"""Unit tests for the doctor's settings and port checks (no values ever shown)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from ops_fakes import FakePorts, FakeRunner, make_ctx, ok
from pydantic import SecretStr
from typani import Ok

from hullbreach_ops import checks_config as cc
from hullbreach_ops import readme_links as rl
from hullbreach_ops.accounts import GAME_KEYS_VAR, GAME_SIDE_KEY_VAR
from hullbreach_ops.checkbase import DoctorRun, Status

PW = "placeholder-db-pw-123"
URL = f"postgresql+psycopg://hullbreach:{PW}@localhost:5432/hullbreach"
KEY = "k" * 40


def _run(tmp_path: Path, environ: dict[str, str], **kw: object) -> DoctorRun:
    return DoctorRun(ctx=make_ctx(tmp_path, environ, **kw))  # type: ignore[arg-type]


def test_env_file_fails_without_env_and_warns_for_terminal_settings(
    tmp_path: Path,
) -> None:
    # frob:tests src/hullbreach_ops/checks_config.py::check_env_file kind="unit"
    missing = cc.check_env_file(_run(tmp_path, {}))
    assert missing.status == Status.FAIL
    assert missing.fix[0] == "Copy the example: cp .env.example .env"
    assert missing.readme == rl.SETTINGS
    from_env = cc.check_env_file(_run(tmp_path, {"HULLBREACH_DATABASE_URL": URL}))
    assert from_env.status == Status.WARN
    run = _run(tmp_path, {})
    (run.ctx.settings.root / ".env").write_text("X=1\n")
    assert cc.check_env_file(run).status == Status.PASS


def test_settings_report_set_or_unset_never_values(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/checks_config.py::check_settings kind="unit"
    unset = cc.check_settings(_run(tmp_path, {}))
    assert unset.status == Status.FAIL
    assert "HULLBREACH_DATABASE_URL, POSTGRES_PASSWORD" in unset.summary
    assert "POSTGRES_PASSWORD: not set" in unset.details
    assert "must equal POSTGRES_PASSWORD" in unset.fix[2]

    monkeypatch.setattr(
        cc, "load_app_config", lambda _s: Ok(SimpleNamespace(database_url=URL))
    )
    env = {
        "HULLBREACH_DATABASE_URL": URL,
        "POSTGRES_PASSWORD": "a-different-pw",
        "HULLBREACH_ADMIN_PASSWORD": "admin-placeholder",
    }
    run = _run(tmp_path, env)
    wrong = cc.check_settings(run)
    assert wrong.status == Status.FAIL
    assert "password inside HULLBREACH_DATABASE_URL differs" in wrong.summary
    shown = " ".join([wrong.summary, *wrong.details, *wrong.fix])
    assert PW not in shown and "a-different-pw" not in shown
    assert run.ctx.console.redact(f"x {PW} y") == "x <redacted> y"

    env["POSTGRES_PASSWORD"] = PW
    assert cc.check_settings(_run(tmp_path, env)).status == Status.PASS
    env["HULLBREACH_ADMIN_PASSWORD"] = "changeme"
    assert "example value" in cc.check_settings(_run(tmp_path, env)).summary
    env["HULLBREACH_DB_PORT"] = "5434"
    port = cc.check_settings(_run(tmp_path, env))
    assert port.summary.startswith("the port in HULLBREACH_DATABASE_URL is 5432")


def test_game_keys_empty_mismatch_short_and_good(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_config.py::check_game_keys kind="unit"
    def check(keys: list[str], env: dict[str, str], profile: str = "full") -> object:
        run = _run(tmp_path, env)
        run.profile = profile
        run.app_config = SimpleNamespace(  # type: ignore[assignment]
            game_server_api_keys=[SecretStr(k) for k in keys]
        )
        return cc.check_game_keys(run)

    assert check([], {}).status == Status.WARN  # type: ignore[attr-defined]
    assert check([], {}, "platform").status == Status.FAIL  # type: ignore[attr-defined]
    wrong = check([KEY], {GAME_SIDE_KEY_VAR: "x" * 40})
    assert wrong.status == Status.FAIL  # type: ignore[attr-defined]
    assert wrong.summary == (  # type: ignore[attr-defined]
        f"{GAME_SIDE_KEY_VAR} is set here but matches none of {GAME_KEYS_VAR}"
    )
    assert check(["short"], {}).status == Status.WARN  # type: ignore[attr-defined]
    good = check([KEY], {GAME_SIDE_KEY_VAR: KEY})
    assert good.status == Status.PASS  # type: ignore[attr-defined]


def test_ports_name_the_program_holding_a_port(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_config.py::check_ports kind="unit"
    runner = FakeRunner(
        replies={
            ("docker", "ps"): ok(
                "other-api|0.0.0.0:8000->8000/tcp\nplatform-db-1|127.0.0.1:5432->5432/tcp\n"
            ),
            ("docker", "compose", "-p", "platform", "ps"): ok(
                '{"Name": "platform-db-1", "State": "running", "Health": "healthy"}'
            ),
        }
    )
    ports = FakePorts(open_ports={5432, 8000})
    result = cc.check_ports(_run(tmp_path, {}, runner=runner, ports=ports))
    assert result.status == Status.FAIL
    assert (
        result.summary
        == "port 8000 (API) is already used by docker container other-api"
    )
    assert "5432 (database): used by this platform" in result.details[0]
    assert "HULLBREACH_PORT=<free port>" in result.fix[1]
    assert result.readme is not None
    assert result.readme.describe().startswith("README 'API problems'")
    free = cc.check_ports(_run(tmp_path, {}, runner=runner, ports=FakePorts()))
    assert free.status == Status.PASS
