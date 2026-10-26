"""Make the platform reachable from other computers on the same network.

`lan` starts the API and website bound to 0.0.0.0, lists this computer's
LAN addresses, and on WSL prints (and, only after a y/N, runs) the Windows
commands that forward the ports and open the firewall. The database stays on
loopback (INV-005): other computers only ever talk to the API and website.
"""

from __future__ import annotations

import base64
import ipaddress
import socket

from pydantic import BaseModel
from typani import Ok, Result, propagate

from hullbreach_ops import lifecycle
from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

LAN_HOST = "0.0.0.0"
FIREWALL_RULE = "Hullbreach platform"
HYPERV_RULE = "HullbreachPlatform"
# The fixed id Windows uses for WSL virtual machines in Hyper-V firewall rules.
WSL_VM_CREATOR_ID = "{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}"
_SKIP_INTERFACES = ("lo", "docker", "br-", "veth", "virbr", "cni", "flannel")


# frob:tests tests/unit/test_ops_lan.py::test_windows_commands_for_nat_and_mirrored
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class WindowsSteps(BaseModel):
    """PowerShell lines (run as Administrator) that open the ports, and their undo."""

    mode: str
    apply: list[str]
    undo: list[str]
    note: str = ""


def _is_lan_address(text: str) -> bool:
    """True for a private or global IPv4 address another computer could reach."""
    try:
        addr = ipaddress.IPv4Address(text)
    except ValueError:
        return False
    return not (addr.is_loopback or addr.is_link_local or addr.is_unspecified)


def _primary_ip() -> str | None:
    """The address the OS would use to reach the internet (no packet is sent)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect(("192.0.2.1", 9))
            address = sock.getsockname()[0]
        except OSError:
            return None
    return address if _is_lan_address(address) else None


# frob:tests tests/unit/test_ops_lan.py::test_lan_ips_filters_container_bridges
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def wsl_ip(ctx: OpsContext) -> str | None:
    """The WSL virtual machine's own address (what Windows forwards to under NAT)."""
    result = ctx.runner.run(["ip", "-4", "-o", "addr", "show", "eth0"], timeout=5)
    if result.is_err or not result.danger_ok.succeeded:
        return None
    for line in result.danger_ok.stdout.splitlines():
        parts = line.split()
        if "inet" in parts:
            return parts[parts.index("inet") + 1].split("/")[0]
    return None


# frob:tests tests/unit/test_ops_lan.py::test_lan_ips_filters_container_bridges
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def lan_ips(ctx: OpsContext) -> list[str]:
    """Addresses other computers on the network can use to reach this one."""
    if ctx.platform.wsl:
        script = (
            "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { "
            "$_.InterfaceAlias -notlike 'vEthernet*' -and "
            "$_.InterfaceAlias -notlike 'Loopback*' } | "
            "ForEach-Object { $_.IPAddress }"
        )
        result = ctx.runner.run(
            ["powershell.exe", "-NoProfile", "-Command", script], timeout=30
        )
        if result.is_ok and result.danger_ok.succeeded:
            found = [
                ip.strip()
                for ip in result.danger_ok.stdout.splitlines()
                if _is_lan_address(ip.strip())
            ]
            _log.info("lan: windows addresses %s", found)
            return found
        _log.warning("lan: could not ask Windows for its addresses")
        return []
    if ctx.platform.system == "Linux":
        result = ctx.runner.run(["ip", "-4", "-o", "addr", "show", "scope", "global"])
        if result.is_ok and result.danger_ok.succeeded:
            found = []
            for line in result.danger_ok.stdout.splitlines():
                parts = line.split()
                if len(parts) < 4 or parts[1].startswith(_SKIP_INTERFACES):
                    continue
                address = parts[3].split("/")[0]
                if _is_lan_address(address):
                    found.append(address)
            _log.info("lan: linux addresses %s", found)
            return found
    primary = _primary_ip()
    return [primary] if primary else []


# frob:tests tests/unit/test_ops_lan.py::test_windows_commands_for_nat_and_mirrored
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def networking_mode(ctx: OpsContext) -> str:
    """WSL's networking mode (`nat` or `mirrored`); "" when not on WSL."""
    if not ctx.platform.wsl:
        return ""
    result = ctx.runner.run(["wslinfo", "--networking-mode"], timeout=10)
    if result.is_ok and result.danger_ok.succeeded:
        mode = result.danger_ok.stdout.strip().lower()
        if mode:
            return mode
    return "nat"


# frob:tests tests/unit/test_ops_lan.py::test_windows_commands_for_nat_and_mirrored
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def windows_steps(mode: str, ports: list[int], target_ip: str | None) -> WindowsSteps:
    """The exact Windows commands that let LAN traffic reach the WSL ports."""
    port_list = ",".join(str(p) for p in ports)
    firewall = (
        f"New-NetFirewallRule -DisplayName '{FIREWALL_RULE}' -Direction Inbound "
        f"-Protocol TCP -LocalPort {port_list} -Action Allow"
    )
    firewall_undo = f"Remove-NetFirewallRule -DisplayName '{FIREWALL_RULE}'"
    if mode == "mirrored":
        return WindowsSteps(
            mode=mode,
            apply=[
                firewall,
                f"New-NetFirewallHyperVRule -Name {HYPERV_RULE} -DisplayName "
                f"'{FIREWALL_RULE}' -Direction Inbound -VMCreatorId "
                f"'{WSL_VM_CREATOR_ID}' -Protocol TCP -LocalPorts {port_list}",
            ],
            undo=[firewall_undo, f"Remove-NetFirewallHyperVRule -Name {HYPERV_RULE}"],
        )
    target = target_ip or "<WSL address from: wsl hostname -I>"
    apply = [
        f"netsh interface portproxy add v4tov4 listenport={p} listenaddress=0.0.0.0 "
        f"connectport={p} connectaddress={target}"
        for p in ports
    ]
    undo = [
        f"netsh interface portproxy delete v4tov4 listenport={p} listenaddress=0.0.0.0"
        for p in ports
    ]
    return WindowsSteps(
        mode="nat",
        apply=[*apply, firewall],
        undo=[*undo, firewall_undo],
        note="WSL gets a new address after a reboot; run `lan` again then.",
    )


def _run_as_admin(ctx: OpsContext, lines: list[str]) -> bool:
    """Run PowerShell lines elevated (Windows shows its own UAC prompt)."""
    script = "; ".join(lines)
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    launcher = (
        "Start-Process powershell -Verb RunAs -Wait -ArgumentList "
        f"'-NoProfile -EncodedCommand {encoded}'"
    )
    result = ctx.runner.run(
        ["powershell.exe", "-NoProfile", "-Command", launcher], timeout=300
    )
    ok = result.is_ok and result.danger_ok.succeeded
    _log.info("lan: elevated windows commands ran=%s", ok)
    return ok


# noqa: E501  # frob:tests tests/unit/test_ops_lan.py::test_lan_starts_on_all_interfaces_and_asks_before_windows_changes
# frob:doc docs/index.md#operator-scripts-and-the-doctor
@propagate
def lan(ctx: OpsContext) -> Result[None, OpsError]:
    """Start bound to 0.0.0.0 and print the URL a friend on the network opens."""
    lifecycle.start(ctx, LAN_HOST).unwrap()
    s = ctx.settings
    ips = lan_ips(ctx)
    ctx.console.heading("Reaching the platform from another computer")
    if not ips:
        ctx.console.line(
            "Could not find this computer's network address. Look it up in your "
            "system's network settings (it usually starts with 192.168. or 10.)."
        )
        ips = ["<this computer's address>"]
    for ip in ips:
        ctx.console.line(f"  Website for a friend:  http://{ip}:{s.web_port}")
        ctx.console.line(f"  Platform URL for a game server:  http://{ip}:{s.api_port}")
    ctx.console.line(
        "Both computers must be on the same network (same Wi-Fi or router)."
    )
    if ctx.platform.wsl:
        mode = networking_mode(ctx)
        steps = windows_steps(mode, [s.web_port, s.api_port], wsl_ip(ctx))
        ctx.console.line()
        ctx.console.line(
            f"This is WSL ({steps.mode} networking): Windows must pass the traffic "
            "on. In PowerShell opened with 'Run as administrator', run:"
        )
        for line in steps.apply:
            ctx.console.line(f"    {line}")
        ctx.console.line("To undo it later:")
        for line in steps.undo:
            ctx.console.line(f"    {line}")
        if steps.note:
            ctx.console.line(steps.note)
        if ctx.console.confirm(
            "Run these Windows commands now (Windows will ask for permission)?"
        ):
            if _run_as_admin(ctx, steps.apply):
                ctx.console.line("Done. Ask your friend to open the website URL above.")
            else:
                ctx.console.line(
                    "The commands did not run (permission refused?). Run them by "
                    "hand as shown above."
                )
    else:
        ctx.console.line(
            "If the friend's browser cannot connect, allow incoming connections "
            f"on TCP ports {s.web_port} and {s.api_port} in this computer's firewall."
        )
    ctx.console.line("Stop with: uv run hullbreach_server stop")
    return Ok(None)
