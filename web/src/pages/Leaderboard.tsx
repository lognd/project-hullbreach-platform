import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "@/api/auth";
import {
  fetchLeaderboard,
  type LeaderboardEntry,
  type LeaderboardResponse,
} from "@/api/leaderboard";
import { useSession } from "@/auth/session";
import { Button, ButtonLink } from "@/components/Button";
import { Loading, Notice } from "@/components/Notice";
import { Page } from "@/components/Page";
import { EmptyState, SkeletonRows } from "@/components/Readout";

/** What the page knows: the board once loaded, whether a request is in flight, and the last failure. */
type BoardState = {
  board: LeaderboardResponse | null;
  loading: boolean;
  error: string | null;
};

const INITIAL: BoardState = { board: null, loading: false, error: null };

/** Column template shared by the rows and the label strip: rank, player, ELO, matches. */
const GRID = "grid-cols-[2.5rem_minmax(0,1fr)_4rem_3rem] sm:grid-cols-[4rem_minmax(0,1fr)_6rem_6rem]";

/** A decorative column-label strip for the rows; aria-hidden and a div so the list keeps one item per player. */
function Columns() {
  return (
    <div
      aria-hidden="true"
      className={`grid gap-x-space-12 px-space-12 font-mono text-font-size-12 uppercase tracking-widest text-muted sm:gap-x-space-16 sm:px-space-16 ${GRID}`}
    >
      <span>Rank</span>
      <span>Player</span>
      <span className="text-right">ELO</span>
      <span className="text-right">Played</span>
    </div>
  );
}

/** One ranked player; the signed-in player's own row gets a cyan border, a "You" tag and aria-current. */
function Row({ entry, mine }: { entry: LeaderboardEntry; mine: boolean }) {
  return (
    <li
      aria-current={mine ? "true" : undefined}
      className={`grid items-baseline gap-x-space-12 border bg-panel px-space-12 py-space-12 sm:gap-x-space-16 sm:px-space-16 ${GRID} ${mine ? "border-accent" : "border-line"}`}
    >
      <span className="font-mono text-font-size-14 tabular-nums text-muted">
        {entry.rank}
      </span>
      <span className="min-w-space-0 wrap-anywhere text-font-size-16 font-medium text-ink">
        {entry.username}
        {mine ? (
          <span className="ml-space-8 border border-accent px-space-4 font-mono text-font-size-12 uppercase tracking-widest text-accent">
            You
          </span>
        ) : null}
      </span>
      <span className="text-right font-mono text-font-size-16 font-semibold tabular-nums text-signal">
        {entry.rating}
      </span>
      <span className="text-right font-mono text-font-size-14 tabular-nums text-muted">
        {entry.matches_played}
      </span>
    </li>
  );
}

// frob:doc docs/index.md#leaderboard-page
/** Leaderboard page: public top players by ELO from GET /api/v1/leaderboard; a signed-in player's row is highlighted, and shown below the list when they rank outside it. */
export function Leaderboard() {
  const session = useSession();
  const token = session?.token ?? null;
  const userId = session?.userId ?? null;
  const [state, setState] = useState<BoardState>(INITIAL);
  // Bumped whenever the load restarts or the page unmounts, so a response that
  // belongs to an earlier request (a StrictMode re-run, a token change) is dropped.
  const generation = useRef(0);

  const load = useCallback(async (): Promise<void> => {
    const mine = generation.current;
    setState((previous) => ({ ...previous, loading: true, error: null }));
    try {
      const board = await fetchLeaderboard(token);
      if (generation.current !== mine) {
        return;
      }
      setState({ board, loading: false, error: null });
    } catch (error) {
      if (generation.current !== mine) {
        return;
      }
      setState((previous) => ({
        ...previous,
        loading: false,
        error:
          error instanceof ApiError
            ? error.detail
            : "Something went wrong. Please try again.",
      }));
    }
  }, [token]);

  useEffect(() => {
    generation.current += 1;
    setState(INITIAL);
    void load();
    return () => {
      generation.current += 1;
    };
  }, [load]);

  const { board, loading, error } = state;
  const outsideTop =
    board?.me != null && !board.entries.some((entry) => entry.user_id === board.me?.user_id);

  return (
    <Page
      crumbs={[{ label: "Leaderboard" }]}
      title="Leaderboard"
      purpose="The top players by current ELO. Every finished match moves the board."
    >
      {board !== null && board.entries.length === 0 ? (
        <EmptyState
          title="No ranked players yet."
          hint="The board fills in as soon as the first match is finished."
          action={
            session === null ? (
              <ButtonLink href="/register" variant="primary">
                Create account
              </ButtonLink>
            ) : undefined
          }
        />
      ) : null}
      {board !== null && board.entries.length > 0 ? (
        <div className="flex flex-col gap-space-8">
          <Columns />
          <ul className="flex flex-col gap-space-4">
            {board.entries.map((entry) => (
              <Row key={entry.user_id} entry={entry} mine={entry.user_id === userId} />
            ))}
          </ul>
          {outsideTop && board.me !== null ? (
            <>
              <p className="font-mono text-font-size-12 uppercase tracking-widest text-muted">
                Your rank
              </p>
              <ul>
                <Row entry={board.me} mine />
              </ul>
            </>
          ) : null}
          <p className="font-mono text-font-size-12 uppercase tracking-widest tabular-nums text-muted">
            {board.entries.length} shown of {board.total_players} ranked
          </p>
        </div>
      ) : null}
      {loading && board === null ? (
        <>
          <Loading label="Loading leaderboard" />
          <SkeletonRows count={8} />
        </>
      ) : null}
      {error !== null ? (
        <Notice tone="error" role="alert">
          <span>{error}</span>
          <Button
            variant="primary"
            disabled={loading}
            onClick={() => {
              void load();
            }}
          >
            Try again
          </Button>
        </Notice>
      ) : null}
    </Page>
  );
}
