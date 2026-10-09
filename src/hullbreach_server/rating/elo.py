"""Pure Elo rating arithmetic (T-0056), per docs/index.md#elo-rating.

Decisions (the Jira story left them open): plain Elo with one fixed
K-factor for every account, a starting rating of 1200, an integer floor
of 100, and a decisive-only result (there is no draw in a Hullbreach
match). No I/O, no database, no clock: callers persist the outcome.
"""

from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict
from typani import Err, ErrorSet, Ok, Result

from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# frob:doc docs/index.md#elo-rating
STARTING_RATING = 1200
# frob:doc docs/index.md#elo-rating
K_FACTOR = 32
# frob:doc docs/index.md#elo-rating
RATING_FLOOR = 100
# A 400-point gap means the stronger side is expected to win 10 times in 11.
_SCALE = 400.0


# frob:doc docs/index.md#elo-rating
class EloError(ErrorSet):
    """Reasons rate_match can fail: an input rating is below the floor."""

    BelowFloor = "a rating is below the rating floor"


# frob:doc docs/index.md#elo-rating
class MatchRatings(BaseModel):
    """The new ratings of the winner and loser of one decisive match."""

    model_config = ConfigDict(frozen=True)

    winner: int
    loser: int


# frob:ticket 01M2H5T11R95CAMMJ91D9VG0S5
# frob:doc docs/index.md#elo-rating
def expected_score(rating: int, opponent: int) -> float:
    """Return the probability in (0, 1) that `rating` beats `opponent`."""
    return 1.0 / (1.0 + 10.0 ** ((opponent - rating) / _SCALE))


# frob:ticket 01M2H5T11R95CAMMJ91D9VG0S5
# frob:doc docs/index.md#elo-rating
def rate_match(winner: int, loser: int) -> Result[MatchRatings, EloError]:
    """Return both new ratings after `winner` beats `loser`.

    The winner gains `K_FACTOR * (1 - expected)` rounded half up, so the
    gain is never negative; the loser loses the same amount but never
    drops below `RATING_FLOOR`.
    """
    if winner < RATING_FLOOR or loser < RATING_FLOOR:
        _log.warning("rate_match: rating below floor (%s, %s)", winner, loser)
        return Err(EloError.BelowFloor)
    gain = math.floor(K_FACTOR * (1.0 - expected_score(winner, loser)) + 0.5)
    result = MatchRatings(winner=winner + gain, loser=max(RATING_FLOOR, loser - gain))
    _log.debug("rate_match: %s beat %s by %s -> %s", winner, loser, gain, result)
    return Ok(result)
