import { apiFetch, bearerHeaders, errorFromResponse, requestJson, type UserProfile } from "@/api/auth";

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
/** GET /api/v1/me with the caller's bearer token (or the session cookie when token is ""); 200 MeResponse on success, 401 rejects with an ApiError. */
export async function fetchMe(token: string, timeoutMs?: number): Promise<MeResponse> {
  return requestJson<MeResponse>(ME_BASE, { headers: bearerHeaders(token) }, timeoutMs);
}

// frob:doc docs/index.md#account-settings-page
/** PATCH /api/v1/me's planned request body (T-0034): only changed fields; email or password changes need `current_password`. */
export type UpdateMeRequest = {
  username?: string;
  email?: string;
  password?: string;
  current_password?: string;
};

// frob:doc docs/index.md#account-settings-page
/** PATCH /api/v1/me with the caller's bearer token; 200 UserProfile on success, 403/409/422 rejects with an ApiError (a `field` names the offender). */
export async function updateMe(
  token: string,
  payload: UpdateMeRequest,
): Promise<UserProfile> {
  return requestJson<UserProfile>(ME_BASE, {
    method: "PATCH",
    headers: { ...bearerHeaders(token), "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
}

// frob:ticket 01M2H5T1168H89BH4V49VR22FC
// frob:doc docs/index.md#account-settings-page
/** DELETE /api/v1/me with the account password; 204 on success (the server clears the session cookie), 403 (wrong password) or 422 rejects with an ApiError. */
export async function deleteMe(token: string, currentPassword: string): Promise<void> {
  const response = await apiFetch(ME_BASE, {
    method: "DELETE",
    headers: { ...bearerHeaders(token), "content-type": "application/json" },
    body: JSON.stringify({ current_password: currentPassword }),
  });
  if (!response.ok) {
    throw await errorFromResponse(response);
  }
}

// frob:doc docs/index.md#match-history-page
/** One page of GET /api/v1/me/matches (planned, T-0059): matches newest first and the cursor for the next page, or null on the last. */
export type MatchPage = {
  items: MatchSummary[];
  next_cursor: string | null;
};

// frob:doc docs/index.md#match-history-page
/** GET /api/v1/me/matches with the caller's bearer token, from `cursor` when given; 200 MatchPage on success, 401 rejects with an ApiError. */
export async function fetchMatches(
  token: string,
  cursor: string | null = null,
): Promise<MatchPage> {
  const query = cursor === null ? "" : `?cursor=${encodeURIComponent(cursor)}`;
  return requestJson<MatchPage>(`${ME_BASE}/matches${query}`, {
    headers: bearerHeaders(token),
  });
}
