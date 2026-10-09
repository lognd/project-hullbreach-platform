"""Unit tests for the pure Elo module (T-0056)."""

from __future__ import annotations

import random

from hullbreach_server.rating.elo import (
    K_FACTOR,
    RATING_FLOOR,
    STARTING_RATING,
    EloError,
    expected_score,
    rate_match,
)


# frob:ticket 01M2H5T11R95CAMMJ91D9VG0S5
# frob:tests src/hullbreach_server/rating/elo.py::expected_score kind="unit"
def test_equal_ratings_are_a_coin_flip() -> None:
    """Equal ratings give an expected score of exactly one half."""
    assert expected_score(1200, 1200) == 0.5


# frob:ticket 01M2H5T11R95CAMMJ91D9VG0S5
# frob:tests src/hullbreach_server/rating/elo.py::rate_match kind="unit"
def test_equal_ratings_move_half_the_k_factor() -> None:
    """Between equals the winner gains K/2 and the loser loses K/2."""
    result = rate_match(STARTING_RATING, STARTING_RATING).unwrap()

    assert result.winner == STARTING_RATING + K_FACTOR // 2
    assert result.loser == STARTING_RATING - K_FACTOR // 2


# frob:ticket 01M2H5T11R95CAMMJ91D9VG0S5
# frob:tests src/hullbreach_server/rating/elo.py::rate_match kind="unit"
def test_upset_moves_more_than_an_expected_win() -> None:
    """The higher-rated side losing changes ratings by more than it winning."""
    upset = rate_match(1200, 1400).unwrap()
    expected = rate_match(1400, 1200).unwrap()

    assert upset.winner - 1200 > expected.winner - 1400


# frob:ticket 01M2H5T11R95CAMMJ91D9VG0S5
# frob:tests src/hullbreach_server/rating/elo.py::rate_match kind="unit"
def test_loser_never_drops_below_the_floor() -> None:
    """A loser at the floor stays at the floor."""
    result = rate_match(1200, RATING_FLOOR).unwrap()

    assert result.loser == RATING_FLOOR


# frob:ticket 01M2H5T11R95CAMMJ91D9VG0S5
# frob:tests src/hullbreach_server/rating/elo.py::rate_match kind="unit"
def test_rating_below_the_floor_is_rejected() -> None:
    """An input rating under the floor is an Err, not a silent clamp."""
    assert rate_match(RATING_FLOOR - 1, 1200).unwrap_err() is EloError.BelowFloor
    assert rate_match(1200, RATING_FLOOR - 1).unwrap_err() is EloError.BelowFloor


def _rating_pairs() -> list[tuple[int, int]]:
    """A grid over the useful rating range plus seeded random pairs, floor edges included."""
    grid = range(RATING_FLOOR, 3001, 100)
    pairs = [(a, b) for a in grid for b in grid]
    rng = random.Random(127)
    pairs += [
        (rng.randint(RATING_FLOOR, 4000), rng.randint(RATING_FLOOR, 4000))
        for _ in range(2000)
    ]
    return pairs


# frob:ticket 01M3DG5Y3ZT86KZDX76GNG69PQ
# frob:tests src/hullbreach_server/rating/elo.py::rate_match kind="unit"
def test_winner_never_loses_rating() -> None:
    """For every sampled pairing, the winner's new rating is at least the old one."""
    for winner, loser in _rating_pairs():
        result = rate_match(winner, loser).unwrap()
        assert result.winner >= winner, (winner, loser, result)


# frob:ticket 01M3DG5Y3ZT86KZDX76GNG69PQ
# frob:tests src/hullbreach_server/rating/elo.py::rate_match kind="unit"
def test_loser_never_gains_rating() -> None:
    """For every sampled pairing, the loser's new rating is at most the old one."""
    for winner, loser in _rating_pairs():
        result = rate_match(winner, loser).unwrap()
        assert result.loser <= loser, (winner, loser, result)
