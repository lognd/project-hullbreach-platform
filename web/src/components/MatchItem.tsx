import type { MatchSummary } from "@/api/me";
import { AppLink } from "@/components/AppLink";

/** Formats whole seconds as m:ss, e.g. 305 -> "5:05". */
export function formatDuration(seconds: number): string {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

/** Formats a rating change with an explicit sign, e.g. 12 -> "+12", -12 -> "-12", 0 -> "0". */
export function formatDelta(delta: number): string {
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

/** Column template shared by the rows and the column-label strip: result, opponent, ELO range, delta, date (sm and up); phones stack it in two lines. */
const GRID =
  "grid-cols-[3rem_minmax(0,1fr)_auto] sm:grid-cols-[4rem_minmax(0,1fr)_9rem_4rem_6rem]";

// frob:doc docs/index.md#player-api-client-and-the-profile-page
/** A decorative column-label strip for a list of MatchItems; aria-hidden and a div (not an li) so the list keeps exactly one item per match. */
export function MatchColumns() {
  return (
    <div
      aria-hidden="true"
      className={`hidden gap-x-space-16 px-space-16 font-mono text-font-size-12 uppercase tracking-widest text-muted sm:grid ${GRID}`}
    >
      <span>Result</span>
      <span>Opponent</span>
      <span className="text-right">ELO</span>
      <span className="text-right">Change</span>
      <span className="text-right">Date</span>
    </div>
  );
}

// frob:doc docs/index.md#player-api-client-and-the-profile-page
/** One match row linking to its detail (result, opponent, ELO range and change, date; `detailed` adds duration and stats); a table-like grid on sm+ and a two-line stack on phones so long names never force horizontal scroll. */
export function MatchItem({
  match,
  detailed = false,
}: {
  match: MatchSummary;
  detailed?: boolean;
}) {
  const won = match.result === "win";
  const tone = won ? "border-l-accent text-accent" : "border-l-signal text-signal";
  const delta = match.rating_after - match.rating_before;
  return (
    <li
      className={`relative grid items-baseline gap-x-space-12 gap-y-space-8 border border-l-4 border-line bg-panel px-space-16 py-space-16 sm:gap-x-space-16 ${GRID} ${tone}`}
    >
      <span className="col-start-1 row-start-1 font-mono text-font-size-12 font-bold uppercase tracking-widest sm:col-auto sm:row-auto">
        {won ? "Win" : "Loss"}
      </span>
      <span className="col-start-2 row-start-1 min-w-space-0 wrap-anywhere text-font-size-16 font-medium text-ink sm:col-auto sm:row-auto">
        {/* frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ */}
        {/* The after: overlay makes the whole row the link target. */}
        <AppLink
          href={`/me/matches/${encodeURIComponent(match.id)}`}
          className="wrap-anywhere after:absolute after:inset-0 hover:text-accent"
        >
          {match.opponent}
        </AppLink>
      </span>{" "}
      <span className="col-start-2 row-start-2 font-mono text-font-size-14 tabular-nums text-muted sm:col-auto sm:row-auto sm:text-right">
        {match.rating_before} {"->"} {match.rating_after}
      </span>
      <span className="col-start-3 row-start-1 text-right font-mono text-font-size-14 font-semibold tabular-nums sm:col-auto sm:row-auto">
        {formatDelta(delta)}
      </span>
      <time
        dateTime={match.played_at}
        className="col-start-3 row-start-2 text-right font-mono text-font-size-14 tabular-nums text-muted sm:col-auto sm:row-auto"
      >
        {match.played_at.slice(0, 10)}
      </time>
      {detailed ? (
        <p className="col-span-full flex flex-wrap gap-x-space-16 gap-y-space-4 border-t border-line pt-space-8 font-mono text-font-size-12 uppercase tracking-wider tabular-nums text-muted">
          <Stat label="time" value={formatDuration(match.duration_seconds)} />
          {Object.entries(match.stats).map(([name, value]) => (
            <Stat key={name} label={name.replaceAll("_", " ")} value={value} />
          ))}
        </p>
      ) : null}
    </li>
  );
}
