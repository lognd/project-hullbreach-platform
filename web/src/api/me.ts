import { bearerHeaders, requestJson, type UserProfile } from "@/api/auth";

/** Base path for the signed-in player's own resources (docs/backlog.md: T-0031, T-0034, T-0059). */
const ME_BASE = "/api/v1/me";

// frob:doc docs/index.md#player-api-client-and-the-profile-page
/** A cosmetic skin the player owns; planned inventory entry of GET /api/v1/me (T-0031). */
export type OwnedSkin = {
  id: string;
  slug: string;
  name: string;
};

// frob:doc docs/index.md#player-api-client-and-the-profile-page
/** One finished match from the player's point of view; shared by the profile's last five and the full history (T-0059). */
export type MatchSummary = {
  id: string;
  played_at: string;
  opponent: string;
  result: "win" | "loss";
  duration_seconds: number;
  rating_before: number;
  rating_after: number;
  stats: Record<string, number>;
};

// frob:doc docs/index.md#player-api-client-and-the-profile-page
/** GET /api/v1/me's planned 200 body: the profile (currency is the balance) plus inventory and the last five matches, newest first (T-0031). */
export type MeResponse = UserProfile & {
  inventory: OwnedSkin[];
  recent_matches: MatchSummary[];
};

// frob:doc docs/index.md#player-api-client-and-the-profile-page
/** GET /api/v1/me with the caller's bearer token; 200 MeResponse on success, 401 rejects with an ApiError. */
export async function fetchMe(token: string): Promise<MeResponse> {
  return requestJson<MeResponse>(ME_BASE, { headers: bearerHeaders(token) });
}
