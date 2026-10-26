import { useEffect, useState } from "react";
import { ApiError } from "@/api/auth";
import { fetchMe, type MeResponse } from "@/api/me";
import { useSession } from "@/auth/session";
import { AppLink } from "@/components/AppLink";
import { Button, ButtonLink } from "@/components/Button";
import { MatchColumns, MatchItem } from "@/components/MatchItem";
import { Loading, Notice } from "@/components/Notice";
import { Page } from "@/components/Page";
import { EmptyState, SkeletonRows, StatTile } from "@/components/Readout";
import { SignInPrompt } from "@/components/SignInPrompt";

/** What the page is showing: waiting on the server, the loaded profile, or a failure message. */
type ProfileState =
  | { status: "loading" }
  | { status: "ready"; me: MeResponse }
  | { status: "error"; message: string };

// frob:doc docs/index.md#player-api-client-and-the-profile-page
/** Profile page: loads GET /api/v1/me for the signed-in player and shows ELO, balance, owned skins and the last five matches in a single column that fits a phone. */
export function Profile() {
  const session = useSession();
  const token = session?.token ?? null;
  const [state, setState] = useState<ProfileState>({ status: "loading" });
  // Bumped by Try again so the effect below refetches.
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (token === null) {
      return;
    }
    let cancelled = false;
    setState({ status: "loading" });
    fetchMe(token)
      .then((me) => {
        if (!cancelled) {
          setState({ status: "ready", me });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setState({
            status: "error",
            message:
              error instanceof ApiError
                ? error.detail
                : "Something went wrong. Please try again.",
          });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [token, attempt]);

  if (token === null) {
    return <SignInPrompt title="Profile" reason="to see your profile." />;
  }

  if (state.status === "error") {
    return (
      <Page eyebrow="Pilot record" title="Profile">
        <Notice tone="error" role="alert">
          <span>{state.message}</span>
          <Button onClick={() => setAttempt((n) => n + 1)}>Try again</Button>
        </Notice>
      </Page>
    );
  }

  if (state.status === "loading") {
    return (
      <Page eyebrow="Pilot record" title="Profile">
        <Loading label="Loading profile" />
        <SkeletonRows count={3} />
      </Page>
    );
  }

  const { me } = state;
  const last = me.recent_matches.slice(0, 5);
  const wins = last.filter((match) => match.result === "win").length;
  const net = last.reduce((sum, match) => sum + match.rating_after - match.rating_before, 0);
  return (
    <Page eyebrow="Pilot record" title={me.username} titleClassName="wrap-anywhere">
      <dl className="grid grid-cols-2 gap-space-8 sm:grid-cols-4">
        <StatTile label="ELO" value={me.rating} tone="accent" />
        <StatTile label="Balance" value={me.currency} />
        {last.length > 0 ? (
          <>
            <StatTile label="Last 5" value={`${wins}-${last.length - wins}`} />
            <StatTile label="Net ELO" value={net > 0 ? `+${net}` : String(net)} tone={net >= 0 ? "ok" : "fail"} />
          </>
        ) : null}
      </dl>

      <section aria-labelledby="profile-skins" className="flex flex-col gap-space-12">
        <h2 id="profile-skins" className="font-mono text-font-size-14 font-semibold uppercase tracking-widest text-muted">
          Owned skins
        </h2>
        {me.inventory.length === 0 ? (
          <EmptyState title="No skins yet." hint="Skins you own will be listed here." />
        ) : (
          <ul className="flex flex-wrap gap-space-8">
            {me.inventory.map((skin) => (
              <li
                key={skin.id}
                className="wrap-anywhere rounded-radius-2 border border-line bg-panel px-space-12 py-space-4 text-font-size-14"
              >
                {skin.name}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="profile-matches" className="flex flex-col gap-space-12">
        <div className="flex flex-wrap items-baseline justify-between gap-space-8">
          <h2 id="profile-matches" className="font-mono text-font-size-14 font-semibold uppercase tracking-widest text-muted">
            Recent matches
          </h2>
          <AppLink href="/me/matches" className="text-font-size-14 font-medium text-accent underline underline-offset-4 hover:text-ink">
            Full history
          </AppLink>
        </div>
        {me.recent_matches.length === 0 ? (
          <EmptyState
            title="No matches yet."
            hint="Your last five results and rating changes will show here."
            action={
              <ButtonLink href="/" variant="primary">
                Back to start
              </ButtonLink>
            }
          />
        ) : (
          <>
            <MatchColumns />
            <ul className="flex flex-col gap-space-4">
              {last.map((match) => (
                <MatchItem key={match.id} match={match} />
              ))}
            </ul>
          </>
        )}
      </section>
    </Page>
  );
}
