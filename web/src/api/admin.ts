import { bearerHeaders, requestJson } from "@/api/auth";

const BASE = "/api/v1/admin";

/** One row of the admin player search. */
export type AdminPlayer = {
  id: string;
  username: string;
  role: string;
  rating: number;
  suspended: boolean;
};

/** A moderation action recorded against a player. */
export type ModerationEntry = {
  action: string;
  reason: string;
  admin_id: string;
  created_at: string;
};

/** A trust event the game server reported for a player. */
export type TrustEventRow = {
  kind: string;
  detail: string;
  match_id: string | null;
  created_at: string;
};

/** The admin detail view of one player. */
export type AdminPlayerDetail = AdminPlayer & {
  email: string;
  balance: number;
  created_at: string;
  suspended_reason: string | null;
  moderation: ModerationEntry[];
  trust_events: TrustEventRow[];
};

/** A catalog item as admins see it, including retirement. */
export type AdminItem = {
  id: string;
  slug: string;
  name: string;
  category: string;
  price: number;
  preview_url: string | null;
  retired: boolean;
};

/** JSON request options for an admin call. */
function init(token: string, method: string, body?: unknown): RequestInit {
  return {
    method,
    headers: {
      ...bearerHeaders(token),
      ...(body === undefined ? {} : { "Content-Type": "application/json" }),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  };
}

/** GET /admin/players?q=; partial, case-insensitive username search. */
export function searchPlayers(token: string, q: string): Promise<AdminPlayer[]> {
  return requestJson<AdminPlayer[]>(
    `${BASE}/players?q=${encodeURIComponent(q)}`,
    init(token, "GET"),
  );
}

/** GET /admin/players/{id}. */
export function fetchPlayer(token: string, id: string): Promise<AdminPlayerDetail> {
  return requestJson<AdminPlayerDetail>(`${BASE}/players/${id}`, init(token, "GET"));
}

/** POST suspend or unsuspend with the required reason. */
export function moderatePlayer(
  token: string,
  id: string,
  action: "suspend" | "unsuspend",
  reason: string,
): Promise<AdminPlayerDetail> {
  return requestJson<AdminPlayerDetail>(
    `${BASE}/players/${id}/${action}`,
    init(token, "POST", { reason }),
  );
}

/** GET /admin/items, retired items included. */
export function listItems(token: string): Promise<AdminItem[]> {
  return requestJson<AdminItem[]>(`${BASE}/items`, init(token, "GET"));
}

/** PATCH /admin/items/{id} with the changed fields. */
export function patchItem(
  token: string,
  id: string,
  patch: { name?: string; price?: number; category?: string },
): Promise<AdminItem> {
  return requestJson<AdminItem>(`${BASE}/items/${id}`, init(token, "PATCH", patch));
}

/** DELETE /admin/items/{id}: retire the item. */
export function retireItem(token: string, id: string): Promise<AdminItem> {
  return requestJson<AdminItem>(`${BASE}/items/${id}`, init(token, "DELETE"));
}
