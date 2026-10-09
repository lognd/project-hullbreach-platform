import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "@/api/auth";
import { fetchMatches, type MatchSummary } from "@/api/me";
import { useSession } from "@/auth/session";
import { MatchItem } from "@/components/MatchItem";
import { SignInPrompt } from "@/components/SignInPrompt";

/** The matches loaded so far, the cursor for the next page (null once exhausted), and whether a request is in flight. */
type HistoryState = {
  matches: MatchSummary[];
  nextCursor: string | null;
  loading: boolean;
  loaded: boolean;
  error: string | null;
};

const INITIAL: HistoryState = {
  matches: [],
  nextCursor: null,
  loading: false,
  loaded: false,
  error: null,
};

// frob:doc docs/index.md#match-history-page
/** Match history page: loads GET /api/v1/me/matches one page at a time and appends the next page when Load more is pressed. */
export function History() {
  const session = useSession();
  const token = session?.token ?? null;
  const [state, setState] = useState<HistoryState>(INITIAL);
  // Bumped whenever the list is reset or the page unmounts, so a response that
  // belongs to an earlier list (a StrictMode re-run, a token change) is dropped.
  const generation = useRef(0);

  const loadPage = useCallback(
    async (cursor: string | null): Promise<void> => {
      if (token === null) {
        return;
      }
      const mine = generation.current;
      setState((previous) => ({ ...previous, loading: true, error: null }));
      try {
        const page = await fetchMatches(token, cursor);
        if (generation.current !== mine) {
          return;
        }
        setState((previous) => ({
          matches: [...previous.matches, ...page.items],
          nextCursor: page.next_cursor,
          loading: false,
          loaded: true,
          error: null,
        }));
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
    },
    [token],
  );

  useEffect(() => {
    generation.current += 1;
    setState(INITIAL);
    void loadPage(null);
    return () => {
      generation.current += 1;
    };
  }, [loadPage]);

  if (token === null) {
    return <SignInPrompt title="Match history" reason="to see your matches." />;
  }

  return (
    <main className="mx-auto flex w-full max-w-[40rem] flex-col gap-space-16 bg-paper px-space-16 py-space-32 text-ink">
      <h1 className="text-font-size-32 font-semibold">Match history</h1>
      {state.loaded && state.matches.length === 0 ? (
        <p className="text-font-size-14 text-muted">No matches yet.</p>
      ) : (
        <ul className="flex flex-col gap-space-8">
          {state.matches.map((match) => (
            <MatchItem key={match.id} match={match} detailed />
          ))}
        </ul>
      )}
      {state.error !== null ? (
        <p role="alert" className="text-font-size-14 text-stress-fail">
          {state.error}
        </p>
      ) : null}
      {state.loading && !state.loaded ? (
        <p className="text-font-size-16 text-muted">Loading...</p>
      ) : null}
      {state.nextCursor !== null || state.error !== null ? (
        <button
          type="button"
          disabled={state.loading}
          onClick={() => {
            void loadPage(state.nextCursor);
          }}
          className="text-font-size-16"
        >
          {state.loaded ? "Load more" : "Try again"}
        </button>
      ) : null}
    </main>
  );
}
