import type { MatchSummary, MeResponse } from "@/api/me";

/** Builds a deterministic match, newest first by index, so list tests can assert order and counts. */
export function makeMatch(index: number): MatchSummary {
  const win = index % 2 === 0;
  return {
    id: `match-${index}`,
    played_at: new Date(Date.UTC(2026, 9, 28) - index * 86_400_000).toISOString(),
    opponent: `rival-${index}`,
    result: win ? "win" : "loss",
    duration_seconds: 300 + index,
    rating_before: 1200 - index * 4,
    rating_after: 1200 - index * 4 + (win ? 12 : -12),
    stats: { damage_dealt: 900 - index, hull_breaches: win ? 3 : 1 },
  };
}

/** A typed GET /api/v1/me response (planned contract, T-0031) for a player with two skins and five matches. */
export const meFixture: MeResponse = {
  id: "user-1",
  username: "flagship",
  email: "flagship@example.com",
  role: "player",
  currency: 450,
  rating: 1236,
  created_at: "2026-01-01T00:00:00Z",
  inventory: [
    { id: "item-1", slug: "ember-hull", name: "Ember Hull" },
    { id: "item-2", slug: "frost-plating", name: "Frost Plating" },
  ],
  recent_matches: [0, 1, 2, 3, 4].map(makeMatch),
};
