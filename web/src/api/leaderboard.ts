import { bearerHeaders, requestJson } from "@/api/auth";

/** Path of the public leaderboard endpoint (T-0062). */
const LEADERBOARD_PATH = "/api/v1/leaderboard";

// frob:doc docs/index.md#leaderboard-page
/** One ranked player: position, name, current ELO and matches played. */
export type LeaderboardEntry = {
  rank: number;
  user_id: string;
  username: string;
  rating: number;
  matches_played: number;
};

// frob:doc docs/index.md#leaderboard-page
/** GET /api/v1/leaderboard's 200 body: the top rows, the signed-in caller's row (null when anonymous or unranked) and the number of ranked players. */
export type LeaderboardResponse = {
  entries: LeaderboardEntry[];
  me: LeaderboardEntry | null;
  total_players: number;
};

// frob:doc docs/index.md#leaderboard-page
/** GET /api/v1/leaderboard; public, and a given `token` only adds the caller's own row; 503 rejects with an ApiError. */
export async function fetchLeaderboard(
  token: string | null = null,
): Promise<LeaderboardResponse> {
  return requestJson<LeaderboardResponse>(
    LEADERBOARD_PATH,
    token === null ? undefined : { headers: bearerHeaders(token) },
  );
}
