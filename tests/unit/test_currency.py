"""Unit tests for earning currency by playing ranked matches (S21)."""

from __future__ import annotations

from hullbreach_server.db.models.ledger import CurrencyLedger
from hullbreach_server.services.currency import LOSS_PAYOUT, WIN_PAYOUT, balance

_URL = "/api/v1/matches"
_ME = "/api/v1/me"


# frob:ticket 01M2H5T125F6FYMXJ9JZXSYE6W
def test_recorded_match_pays_both_players(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """Given a recorded match, the winner and the loser each gain their fixed payout."""
    _headers, winner, loser = pilots
    assert balance(db_session, winner.id) == 0

    response = client.post(_URL, json=report(winner, loser), headers=server_key_headers)

    assert response.status_code == 201
    assert balance(db_session, winner.id) == WIN_PAYOUT
    assert balance(db_session, loser.id) == LOSS_PAYOUT
    assert db_session.query(CurrencyLedger).count() == 2


# frob:ticket 01M2H5T125F6FYMXJ9JZXSYE6W
def test_replayed_match_pays_once(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """Given the same match reported twice, the payout is credited exactly once."""
    _headers, winner, loser = pilots
    body = report(winner, loser)

    client.post(_URL, json=body, headers=server_key_headers)
    second = client.post(_URL, json=body, headers=server_key_headers)

    assert second.status_code == 200
    assert balance(db_session, winner.id) == WIN_PAYOUT
    assert balance(db_session, loser.id) == LOSS_PAYOUT
    assert db_session.query(CurrencyLedger).count() == 2


# frob:ticket 01M2H5T125F6FYMXJ9JZXSYE6W
def test_profile_balance_is_the_sum_of_earnings(
    client, server_key_headers, pilots, report
) -> None:
    """Given two matches, GET /me shows the summed earnings as `currency`."""
    headers, flagship, rival = pilots
    client.post(_URL, json=report(flagship, rival), headers=server_key_headers)
    client.post(_URL, json=report(rival, flagship), headers=server_key_headers)

    profile = client.get(_ME, headers=headers).json()

    assert profile["currency"] == WIN_PAYOUT + LOSS_PAYOUT


# frob:ticket 01M2H5T125F6FYMXJ9JZXSYE6W
def test_rejected_match_pays_nothing(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """Given a report naming an unknown player, no ledger row is written."""
    _headers, winner, loser = pilots
    body = report(winner, loser)
    body["players"][1]["user_id"] = "00000000-0000-4000-8000-000000000000"

    response = client.post(_URL, json=body, headers=server_key_headers)

    assert response.status_code == 404
    assert db_session.query(CurrencyLedger).count() == 0
