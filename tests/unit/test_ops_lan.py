"""Unit tests for LAN hosting: addresses, Windows commands and consent."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from ops_fakes import FakeRunner, make_ctx, ok, output
from typani import Ok

from hullbreach_ops import lan
from hullbreach_ops.console import Console
from hullbreach_ops.settings import PlatformInfo

WSL = PlatformInfo(system="Linux", release="6.6-microsoft-standard-WSL2", wsl=True)

IP_ADDR = """\
2: eth0    inet 192.168.1.20/24 brd 192.168.1.255 scope global eth0
3: docker0    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
4: br-1a2b    inet 172.18.0.1/16 brd 172.18.255.255 scope global br-1a2b
5: wlan0    inet 10.0.0.7/8 brd 10.255.255.255 scope global wlan0
"""


def test_lan_ips_filters_container_bridges(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/lan.py::lan_ips kind="unit"
    # frob:tests src/hullbreach_ops/lan.py::wsl_ip kind="unit"
    runner = FakeRunner(replies={("ip", "-4", "-o", "addr", "show"): ok(IP_ADDR)})
    assert lan.lan_ips(make_ctx(tmp_path, runner=runner)) == [
        "192.168.1.20",
        "10.0.0.7",
    ]
    windows = FakeRunner(
        replies={
            ("powershell.exe",): ok("127.0.0.1\r\n192.168.1.50\r\n169.254.3.4\r\n")
        }
    )
    assert lan.lan_ips(make_ctx(tmp_path, runner=windows, platform=WSL)) == [
        "192.168.1.50"
    ]
    eth0 = FakeRunner(
        replies={("ip",): ok("2: eth0    inet 172.29.1.5/20 brd x scope global eth0\n")}
    )
    assert lan.wsl_ip(make_ctx(tmp_path, runner=eth0)) == "172.29.1.5"


def test_windows_commands_for_nat_and_mirrored(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/lan.py::windows_steps kind="unit"
    # frob:tests src/hullbreach_ops/lan.py::WindowsSteps kind="unit"
    # frob:tests src/hullbreach_ops/lan.py::networking_mode kind="unit"
    nat = lan.windows_steps("nat", [5173, 8000], "172.29.1.5")
    assert nat.apply[0] == (
        "netsh interface portproxy add v4tov4 listenport=5173 listenaddress=0.0.0.0 "
        "connectport=5173 connectaddress=172.29.1.5"
    )
    assert "-LocalPort 5173,8000" in nat.apply[-1]
    assert len(nat.undo) == 3
    assert "reboot" in nat.note
    assert "<WSL address" in lan.windows_steps("nat", [8000], None).apply[0]

    mirrored = lan.windows_steps("mirrored", [5173, 8000], None)
    assert not any("portproxy" in line for line in mirrored.apply)
    assert lan.WSL_VM_CREATOR_ID in mirrored.apply[1]

    assert lan.networking_mode(make_ctx(tmp_path)) == ""
    runner = FakeRunner(replies={("wslinfo",): ok("Mirrored\n")})
    assert lan.networking_mode(make_ctx(tmp_path, runner=runner, platform=WSL)) == (
        "mirrored"
    )
    failing = FakeRunner(replies={("wslinfo",): ok("", returncode=1)})
    assert lan.networking_mode(make_ctx(tmp_path, runner=failing, platform=WSL)) == (
        "nat"
    )


def test_lan_starts_on_all_interfaces_and_asks_before_windows_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/lan.py::lan kind="unit"
    hosts: list[str | None] = []

    def fake_start(_ctx: object, host: str | None = None) -> Ok[None]:
        hosts.append(host)
        return Ok(None)

    monkeypatch.setattr("hullbreach_ops.lan.lifecycle.start", fake_start)
    runner = FakeRunner(
        replies={
            ("powershell.exe", "-NoProfile", "-Command"): ok("192.168.1.50\n"),
            ("wslinfo",): ok("nat\n"),
            ("ip",): ok("2: eth0    inet 172.29.1.5/20 scope global eth0\n"),
        }
    )
    ctx = make_ctx(tmp_path, runner=runner, platform=WSL)
    assert lan.lan(ctx).is_ok
    assert hosts == ["0.0.0.0"]
    text = output(ctx)
    assert "Website for a friend:  http://192.168.1.50:5173" in text
    assert "Platform URL for a game server:  http://192.168.1.50:8000" in text
    assert "connectaddress=172.29.1.5" in text
    # Non-interactive means "no": nothing was run as administrator.
    assert not any("RunAs" in " ".join(call) for call in runner.calls)

    agreed = make_ctx(
        tmp_path,
        runner=runner,
        platform=WSL,
        console=Console(io.StringIO(), interactive=True, ask=lambda _q: "y"),
    )
    assert lan.lan(agreed).is_ok
    assert any("RunAs" in " ".join(call) for call in runner.calls)
    assert "Done. Ask your friend" in output(agreed)
