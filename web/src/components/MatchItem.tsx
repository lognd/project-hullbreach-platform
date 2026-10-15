import type { MatchSummary } from "@/api/me";

/** Formats whole seconds as m:ss, e.g. 305 -> "5:05". */
function formatDuration(seconds: number): string {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

/** Formats a rating change with an explicit sign, e.g. 12 -> "+12", -12 -> "-12", 0 -> "0". */
function formatDelta(delta: number): string {
  return delta > 0 ? `+${delta}` : String(delta);
}

/** One "label value" readout in the detailed stats line. */
function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <span>
      {label} <span className="text-ink">{value}</span>
    </span>
  );
}

// frob:doc docs/index.md#player-api-client-and-the-profile-page
/** One match row (opponent, result, date, ELO change; `detailed` adds duration and stats); wraps on narrow screens so long names never force horizontal scroll. */
export function MatchItem({
  match,
  detailed = false,
}: {
  match: MatchSummary;
  detailed?: boolean;
}) {
  const won = match.result === "win";
  const tone = won ? "border-stress-ok text-stress-ok" : "border-stress-fail text-stress-fail";
  const delta = match.rating_after - match.rating_before;
  return (
    <li className={`flex flex-wrap items-baseline gap-x-space-16 gap-y-space-4 border-l-4 bg-panel px-space-16 py-space-12 ${tone}`}>
      <span className="w-full min-w-space-0 wrap-anywhere text-font-size-16 font-medium text-ink sm:w-auto sm:flex-1">
        {match.opponent}
      </span>
      <span className="font-mono text-font-size-12 font-bold uppercase tracking-widest">
        {won ? "Win" : "Loss"}
      </span>
      <span className="font-mono text-font-size-14 tabular-nums text-muted">
        {match.rating_before} {"->"} {match.rating_after}
      </span>
      <span className="font-mono text-font-size-14 font-semibold tabular-nums">{formatDelta(delta)}</span>
      <time dateTime={match.played_at} className="font-mono text-font-size-14 tabular-nums text-muted">
        {match.played_at.slice(0, 10)}
      </time>
      {detailed ? (
        <p className="flex w-full flex-wrap gap-x-space-16 gap-y-space-4 font-mono text-font-size-12 uppercase tracking-wider tabular-nums text-muted">
          <Stat label="time" value={formatDuration(match.duration_seconds)} />
          {Object.entries(match.stats).map(([name, value]) => (
            <Stat key={name} label={name.replaceAll("_", " ")} value={value} />
          ))}
        </p>
      ) : null}
    </li>
  );
}
