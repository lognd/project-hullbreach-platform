"""Unit test for the redacted support bundle."""

from __future__ import annotations

import zipfile
from pathlib import Path

from ops_fakes import make_ctx

from hullbreach_ops.collect import collect


def test_collect_bundles_redacted_output_and_logs_but_never_env(
    tmp_path: Path,
) -> None:
    # frob:tests src/hullbreach_ops/collect.py::collect kind="unit"
    ctx = make_ctx(tmp_path)
    root = ctx.settings.root
    (root / ".env").write_text("POSTGRES_PASSWORD=placeholder-env-pw\n")
    ctx.console.add_secret("placeholder-db-pw")
    ctx.console.line("[FAIL] db-connect  rejected placeholder-db-pw")
    logs = ctx.settings.logs_dir
    logs.mkdir(parents=True)
    (logs / "api.log").write_text(
        "connecting postgresql://hullbreach:placeholder-db-pw@localhost/db\n"
        "token=placeholder-token-value ok\n"
    )

    path = collect(ctx).danger_ok
    assert path.parent == root
    assert path.name == "hullbreach-support-20261015-123000.zip"
    with zipfile.ZipFile(path) as bundle:
        names = bundle.namelist()
        text = "".join(bundle.read(name).decode() for name in names)
    assert sorted(names) == ["doctor-output.txt", "logs/api.log", "system.txt"]
    assert "rejected <redacted>" in text
    assert ".env present: True" in text
    for secret in (
        "placeholder-db-pw",
        "placeholder-token-value",
        "placeholder-env-pw",
    ):
        assert secret not in text
