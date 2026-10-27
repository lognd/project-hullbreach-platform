import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ApiError } from "@/api/auth";
import { fetchMatch, type MatchDetail as MatchDetailBody, type PlayerLine } from "@/api/me";
import { useSession } from "@/auth/session";
import { ButtonLink } from "@/components/Button";
import { formatDelta, formatDuration } from "@/components/MatchItem";
import { Loading, Notice } from "@/components/Notice";
import { Page } from "@/components/Page";
import { SignInPrompt } from "@/components/SignInPrompt";

/** What the page knows: the match once loaded, or why it could not be. */
type DetailState =
  | { phase: "loading" }
  | { phase: "ready"; match: MatchDetailBody }
  | { phase: "error"; message: string };

/** One player's row: name (You for the caller), outcome, rating range and change, and the counters. */
function PlayerRow({ player }: { player: PlayerLine }) {
  const tone = player.won ? "border-l-accent" : "border-l-signal";
  return (
    <li
      className={`flex flex-col gap-space-8 border border-l-4 border-line bg-panel px-space-16 py-space-16 ${tone}`}
    >
      <div className="flex flex-wrap items-baseline justify-between gap-x-space-16 gap-y-space-4">
        <span className="min-w-space-0 wrap-anywhere text-font-size-16 font-medium text-ink">
          {player.username}
          {player.is_you ? (
            <span className="ml-space-8 font-mono text-font-size-12 uppercase tracking-widest text-accent">
              You
            </span>
          ) : null}
        </span>
        <span className="font-mono text-font-size-14 tabular-nums text-muted">
          {player.won ? "Win" : "Loss"} {player.rating_before} {"->"} {player.rating_after}{" "}
          <span className="font-semibold text-ink">{formatDelta(player.rating_delta)}</span>
        </span>
      </div>
      <p className="flex flex-wrap gap-x-space-16 gap-y-space-4 border-t border-line pt-space-8 font-mono text-font-size-12 uppercase tracking-wider tabular-nums text-muted">
        {Object.entries(player.stats).map(([name, value]) => (
          <span key={name}>
            {name.replaceAll("_", " ")} <span className="text-ink">{value}</span>
          </span>
        ))}
      </p>
    </li>
  );
}

// frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
// frob:doc docs/index.md#match-history-page
/** Match detail page: loads GET /api/v1/me/matches/{matchId} and shows the result, duration, your ELO move and both players' lines. */
export function MatchDetail() {
  const session = useSession();
  const token = session?.token ?? null;
  const { matchId = "" } = useParams();
  const [state, setState] = useState<DetailState>({ phase: "loading" });

  useEffect(() => {
    if (token === null) {
      return;
    }
    let current = true;
    setState({ phase: "loading" });
    fetchMatch(token, matchId)
      .then((match) => {
        if (current) {
          setState({ phase: "ready", match });
        }
      })
      .catch((error: unknown) => {
        if (current) {
          setState({
            phase: "error",
            message:
              error instanceof ApiError
                ? error.detail
                : "Something went wrong. Please try again.",
          });
        }
      });
    return () => {
      current = false;
    };
  }, [token, matchId]);

  if (token === null) {
    return <SignInPrompt title="Match" reason="to see this match." />;
  }

  const crumbs = [
    { label: "Profile", href: "/me" },
    { label: "Matches", href: "/me/matches" },
    { label: "Match" },
  ];

  if (state.phase === "ready") {
    const { match } = state;
    return (
      <Page
        crumbs={crumbs}
        title={match.result === "win" ? "Victory" : "Defeat"}
        purpose={`Against ${match.opponent}, ${match.played_at.slice(0, 10)}.`}
      >
        <dl className="flex flex-wrap gap-x-space-32 gap-y-space-12 font-mono text-font-size-14 uppercase tracking-wider text-muted">
          <div>
            <dt className="text-font-size-12">Duration</dt>
            <dd className="text-font-size-24 tabular-nums text-ink">
              {formatDuration(match.duration_seconds)}
            </dd>
          </div>
          <div>
            <dt className="text-font-size-12">ELO</dt>
            <dd className="text-font-size-24 tabular-nums text-ink">
              {match.rating_before} {"->"} {match.rating_after}
            </dd>
          </div>
          <div>
            <dt className="text-font-size-12">Change</dt>
            <dd data-testid="your-delta" className="text-font-size-24 tabular-nums text-ink">
              {formatDelta(match.rating_delta)}
            </dd>
          </div>
        </dl>
        <ul className="flex flex-col gap-space-4">
          {match.players.map((player) => (
            <PlayerRow key={player.username} player={player} />
          ))}
        </ul>
        <div>
          <ButtonLink href="/me/matches">Back to matches</ButtonLink>
        </div>
      </Page>
    );
  }

  return (
    <Page crumbs={crumbs} title="Match" purpose="One finished match in full.">
      {state.phase === "loading" ? (
        <Loading label="Loading match" />
      ) : (
        <>
          <Notice tone="error" role="alert">
            <span>{state.message}</span>
          </Notice>
          <div>
            <ButtonLink href="/me/matches">Back to matches</ButtonLink>
          </div>
        </>
      )}
    </Page>
  );
}
