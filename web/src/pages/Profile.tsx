import { useEffect, useState } from "react";
import { ApiError } from "@/api/auth";
import { fetchMe, type MeResponse } from "@/api/me";
import { useSession } from "@/auth/session";
import { MatchItem } from "@/components/MatchItem";

/** What the page is showing: waiting on the server, the loaded profile, or a failure message. */
type ProfileState =
  | { status: "loading" }
  | { status: "ready"; me: MeResponse }
  | { status: "error"; message: string };

// frob:doc docs/index.md#player-api-client-and-the-profile-page
/** Profile page: loads GET /api/v1/me for the signed-in player and shows rating, currency, owned skins and the last five matches in a single column that fits a phone. */
export function Profile() {
  const session = useSession();
  const token = session?.token ?? null;
  const [state, setState] = useState<ProfileState>({ status: "loading" });

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
  }, [token]);

  if (token === null) {
    return (
      <main className="flex flex-col items-center gap-space-8 bg-paper px-space-16 py-space-48 text-ink">
        <h1 className="text-font-size-32 font-semibold">Profile</h1>
        <p className="text-font-size-16 text-muted">
          <a href="/login" className="text-accent">
            Log in
          </a>{" "}
          to see your profile.
        </p>
      </main>
    );
  }

  if (state.status === "error") {
    return (
      <main className="flex flex-col items-center gap-space-8 bg-paper px-space-16 py-space-48 text-ink">
        <h1 className="text-font-size-32 font-semibold">Profile</h1>
        <p role="alert" className="text-font-size-14 text-stress-fail">
          {state.message}
        </p>
      </main>
    );
  }

  if (state.status === "loading") {
    return (
      <main className="flex flex-col items-center gap-space-8 bg-paper px-space-16 py-space-48 text-ink">
        <h1 className="text-font-size-32 font-semibold">Profile</h1>
        <p className="text-font-size-16 text-muted">Loading...</p>
      </main>
    );
  }

  const { me } = state;
  return (
    <main className="mx-auto flex w-full max-w-[40rem] flex-col gap-space-24 bg-paper px-space-16 py-space-32 text-ink">
      <h1 className="wrap-anywhere text-font-size-32 font-semibold">
        {me.username}
      </h1>
      <dl className="flex flex-wrap gap-space-24">
        <div className="flex flex-col gap-space-4">
          <dt className="text-font-size-14 text-muted">Rating</dt>
          <dd className="text-font-size-24 font-semibold">{me.rating}</dd>
        </div>
        <div className="flex flex-col gap-space-4">
          <dt className="text-font-size-14 text-muted">Currency</dt>
          <dd className="text-font-size-24 font-semibold">{me.currency}</dd>
        </div>
      </dl>

      <section aria-labelledby="profile-skins" className="flex flex-col gap-space-8">
        <h2 id="profile-skins" className="text-font-size-20 font-semibold">
          Owned skins
        </h2>
        {me.inventory.length === 0 ? (
          <p className="text-font-size-14 text-muted">No skins yet.</p>
        ) : (
          <ul className="flex flex-wrap gap-space-8">
            {me.inventory.map((skin) => (
              <li
                key={skin.id}
                className="wrap-anywhere rounded-radius-8 bg-panel px-space-12 py-space-4 text-font-size-14"
              >
                {skin.name}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="profile-matches" className="flex flex-col gap-space-8">
        <h2 id="profile-matches" className="text-font-size-20 font-semibold">
          Recent matches
        </h2>
        {me.recent_matches.length === 0 ? (
          <p className="text-font-size-14 text-muted">No matches yet.</p>
        ) : (
          <ul className="flex flex-col gap-space-8">
            {me.recent_matches.slice(0, 5).map((match) => (
              <MatchItem key={match.id} match={match} />
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
