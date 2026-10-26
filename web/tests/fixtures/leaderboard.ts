import type { LeaderboardEntry, LeaderboardResponse } from "@/api/leaderboard";

/** The ranked player at `rank` (1-based): "pilot-<rank>" with descending ELO. */
export function makeEntry(rank: number): LeaderboardEntry {
  return {
    rank,
    user_id: `user-${rank}`,
    username: `pilot-${rank}`,
    rating: 1500 - rank * 10,
    matches_played: 20 - rank,
  };
}

/** A board of `count` top entries out of `total` ranked players, with an optional caller row. */
export function makeBoard(
  count: number,
  total: number = count,
  me: LeaderboardEntry | null = null,
): LeaderboardResponse {
  return {
    entries: Array.from({ length: count }, (_, index) => makeEntry(index + 1)),
    me,
    total_players: total,
  };
}
