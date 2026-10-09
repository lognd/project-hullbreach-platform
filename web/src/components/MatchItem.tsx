import type { MatchSummary } from "@/api/me";

// frob:doc docs/index.md#player-api-client-and-the-profile-page
/** One match row (opponent, result, date, rating change); wraps on narrow screens so long names never force horizontal scroll. */
export function MatchItem({ match }: { match: MatchSummary }) {
  const won = match.result === "win";
  return (
    <li className="flex flex-wrap items-baseline justify-between gap-x-space-16 gap-y-space-4 rounded-radius-8 bg-panel px-space-16 py-space-12">
      <span className="wrap-anywhere text-font-size-16">{match.opponent}</span>
      <span className={won ? "text-stress-ok" : "text-stress-fail"}>
        {won ? "Win" : "Loss"}
      </span>
      <span className="text-font-size-14 text-muted">
        {match.rating_before} {"->"} {match.rating_after}
      </span>
      <time dateTime={match.played_at} className="text-font-size-14 text-muted">
        {match.played_at.slice(0, 10)}
      </time>
    </li>
  );
}
