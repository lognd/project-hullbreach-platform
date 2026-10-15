import { useEffect, useState } from "react";
import { ApiError } from "@/api/auth";
import { fetchMe, type MeResponse } from "@/api/me";
import { useSession } from "@/auth/session";
import { AppLink } from "@/components/AppLink";
import { Button } from "@/components/Button";
import { MatchItem } from "@/components/MatchItem";
import { Loading, Notice } from "@/components/Notice";
import { Page } from "@/components/Page";
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
      </Page>
    );
  }

  const { me } = state;
  return (
    <Page eyebrow="Pilot record" title={me.username} titleClassName="wrap-anywhere">
      <dl className="grid grid-cols-2 gap-space-4 sm:max-w-[28rem]">
        <div className="flex flex-col gap-space-4 bg-panel px-space-16 py-space-12">
          <dt className="font-mono text-font-size-12 uppercase tracking-widest text-muted">ELO</dt>
          <dd className="font-mono text-font-size-32 font-semibold tabular-nums text-accent">{me.rating}</dd>
        </div>
        <div className="flex flex-col gap-space-4 bg-panel px-space-16 py-space-12">
          <dt className="font-mono text-font-size-12 uppercase tracking-widest text-muted">Balance</dt>
          <dd className="font-mono text-font-size-32 font-semibold tabular-nums">{me.currency}</dd>
        </div>
      </dl>

      <section aria-labelledby="profile-skins" className="flex flex-col gap-space-12">
        <h2 id="profile-skins" className="font-mono text-font-size-14 font-semibold uppercase tracking-widest text-muted">
          Owned skins
        </h2>
        {me.inventory.length === 0 ? (
          <p className="text-font-size-14 text-muted">No skins yet.</p>
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
          <p className="text-font-size-14 text-muted">No matches yet.</p>
        ) : (
          <ul className="flex flex-col gap-space-4">
            {me.recent_matches.slice(0, 5).map((match) => (
              <MatchItem key={match.id} match={match} />
            ))}
          </ul>
        )}
      </section>
    </Page>
  );
}
