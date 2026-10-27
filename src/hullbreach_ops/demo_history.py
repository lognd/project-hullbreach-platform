"""The demo's match histories: who played whom, who won and how it went.

Every demo account gets several rated matches against more than one
opponent, with a mix of wins and losses, so the history page and the
match detail have something real to show. Ids are derived from a fixed
key, so seeding is replayable.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict

from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger
from hullbreach_server.services.matches import MatchReport, PlayerReport

_log = get_logger(__name__)

# Namespace for the demo matches' fixed ids, so seeding is replayable.
_NAMESPACE = uuid.UUID("6f1c1f0e-5d0a-4c53-9a53-0d3e6a1b7c10")

_DAY = 60 * 24


# frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
class DemoMatch(BaseModel):
    """One scripted demo match between two demo accounts."""

    model_config = ConfigDict(frozen=True)

    key: str
    player_a: str
    player_b: str
    a_won: bool
    minutes_ago: int
    duration_seconds: int
    a_damage: int
    b_damage: int


def _m(
    key: str,
    a: str,
    b: str,
    a_won: bool,
    minutes_ago: int,
    duration: int,
    a_damage: int,
    b_damage: int,
) -> DemoMatch:
    """Shorthand constructor that keeps the table below readable."""
    return DemoMatch(
        key=key,
        player_a=a,
        player_b=b,
        a_won=a_won,
        minutes_ago=minutes_ago,
        duration_seconds=duration,
        a_damage=a_damage,
        b_damage=b_damage,
    )


# Oldest first: ratings are computed in this order. match-0..5 are the
# original demo_pilot history and keep their ids.
_P, _R, _A, _C = "demo_pilot", "demo_rival", "demo_ace", "demo_cadet"

# frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
# frob:doc docs/index.md#one-command-demo
DEMO_MATCHES: tuple[DemoMatch, ...] = (
    _m("match-0", _P, _R, True, _DAY * 6, 412, 900, 300),
    _m("match-6", _R, _A, True, _DAY * 6 - 240, 590, 760, 520),
    _m("match-1", _P, _A, False, _DAY * 5, 655, 410, 1100),
    _m("match-7", _A, _C, True, _DAY * 5 - 300, 470, 1250, 200),
    _m("match-2", _P, _R, True, _DAY * 4, 388, 1050, 270),
    _m("match-8", _R, _C, True, _DAY * 4 - 200, 360, 980, 330),
    _m("match-3", _P, _R, False, _DAY * 3, 721, 620, 980),
    _m("match-9", _C, _P, False, _DAY * 3 - 400, 300, 180, 1100),
    _m("match-4", _P, _A, True, _DAY * 2, 502, 1300, 640),
    _m("match-10", _A, _R, True, _DAY * 2 - 600, 610, 1180, 940),
    _m("match-11", _C, _A, True, _DAY + 120, 540, 870, 810),
    _m("match-5", _P, _R, True, _DAY, 340, 870, 150),
    _m("match-12", _P, _C, False, 600, 450, 320, 690),
    _m("match-13", _P, _A, True, 180, 700, 1400, 1250),
)

# The accounts the history needs, in the order they are created.
DEMO_ACCOUNT_NAMES = (_P, _R, _A, _C)


def _player(user_id: uuid.UUID, damage: int, alive: int) -> PlayerReport:
    """One demo player's counters, derived from their damage."""
    return PlayerReport(
        user_id=user_id,
        damage_dealt=damage,
        blocks_destroyed=damage // 60,
        blocks_placed=damage // 45,
        time_alive_seconds=alive,
    )


# frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
# noqa: E501  # frob:tests tests/unit/test_ops_demo.py::test_demo_history_is_chronological_with_unique_ids
def build_reports(users: dict[str, User]) -> list[tuple[MatchReport, int]]:
    """The demo history as (report, minutes ago) pairs with fixed match ids."""
    reports: list[tuple[MatchReport, int]] = []
    for match in DEMO_MATCHES:
        a, b = users[match.player_a], users[match.player_b]
        seconds = match.duration_seconds
        reports.append(
            (
                MatchReport(
                    match_id=uuid.uuid5(_NAMESPACE, match.key),
                    winner_id=a.id if match.a_won else b.id,
                    duration_seconds=seconds,
                    players=[
                        _player(a.id, match.a_damage, seconds - 20 * match.a_won),
                        _player(b.id, match.b_damage, seconds - 20 * (not match.a_won)),
                    ],
                ),
                match.minutes_ago,
            )
        )
    _log.debug("demo: built %d scripted match reports", len(reports))
    return reports
