import { useEffect, useState } from "react";
import { ApiError } from "@/api/auth";
import { fetchMe, type MeResponse } from "@/api/me";
import { useSession } from "@/auth/session";
import { Button, ButtonLink } from "@/components/Button";
import { MatchColumns, MatchItem } from "@/components/MatchItem";
import { Loading, Notice } from "@/components/Notice";
import { Page } from "@/components/Page";
import { EloTrace } from "@/components/EloTrace";
import {
  EmptyState,
  Panel,
  SectionHeading,
  SkeletonRows,
  StatTile,
} from "@/components/Readout";
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
      <Page
        crumbs={[{ label: "Profile" }]}
        title="Profile"
        purpose="Your rating, skins and latest results."
      >
        <Notice tone="error" role="alert">
          <span>{state.message}</span>
          <Button onClick={() => setAttempt((n) => n + 1)}>Try again</Button>
        </Notice>
      </Page>
    );
  }

  if (state.status === "loading") {
    return (
      <Page
        crumbs={[{ label: "Profile" }]}
        title="Profile"
        purpose="Your rating, skins and latest results."
      >
        <Loading label="Loading profile" />
        <SkeletonRows count={3} />
      </Page>
    );
  }

  const { me } = state;
  const last = me.recent_matches.slice(0, 5);
  const wins = last.filter((match) => match.result === "win").length;
  const net = last.reduce(
    (sum, match) => sum + match.rating_after - match.rating_before,
    0,
  );
  // recent_matches is newest first; the trace reads oldest to newest.
  const chronological = [...me.recent_matches].reverse();
  const ratings =
    chronological.length > 0
      ? [
          chronological[0].rating_before,
          ...chronological.map((match) => match.rating_after),
        ]
      : [];
  return (
    <Page
      crumbs={[{ label: "Profile" }]}
      title={me.username}
      purpose="Your rating, skins and latest results."
      titleClassName="wrap-anywhere"
    >
      <Panel
        label="ELO"
        tone="primary"
        className="grid gap-space-24 p-space-24 sm:grid-cols-[auto_1fr] sm:items-center"
      >
        <dl>
          <StatTile label="Rating" value={me.rating} tone="signal" size="large" />
        </dl>
        <EloTrace ratings={ratings} />
      </Panel>

      <Panel label="Summary" className="p-space-24">
        <dl className="grid grid-cols-2 gap-space-16 sm:grid-cols-3">
          {last.length > 0 ? (
            <>
              <StatTile label="Last 5" value={`${wins}-${last.length - wins}`} />
              <StatTile
                label="Net ELO"
                value={net > 0 ? `+${net}` : String(net)}
                tone={net >= 0 ? "ok" : "fail"}
              />
            </>
          ) : null}
          <StatTile label="Balance" value={me.currency} />
        </dl>
      </Panel>

      <section aria-labelledby="profile-skins" className="flex flex-col gap-space-12">
        <SectionHeading id="profile-skins">Owned skins</SectionHeading>
        {me.inventory.length === 0 ? (
          <EmptyState title="No skins yet." hint="Skins you own will be listed here." />
        ) : (
          <ul className="flex flex-wrap gap-space-8">
            {me.inventory.map((skin) => (
              <li
                key={skin.id}
                className="wrap-anywhere border border-line bg-panel px-space-12 py-space-8 text-font-size-14"
              >
                {skin.name}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="profile-matches" className="flex flex-col gap-space-12">
        <SectionHeading id="profile-matches">Recent matches</SectionHeading>
        {me.recent_matches.length === 0 ? (
          <EmptyState
            title="No matches yet."
            hint="Your last five results and rating changes will show here."
          />
        ) : (
          <>
            <MatchColumns />
            <ul className="flex flex-col gap-space-4">
              {last.map((match) => (
                <MatchItem key={match.id} match={match} />
              ))}
            </ul>
            <div>
              <ButtonLink href="/me/matches" variant="primary">
                View match history
              </ButtonLink>
            </div>
          </>
        )}
      </section>
    </Page>
  );
}
