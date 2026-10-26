import { Page } from "@/components/Page";
import { PolicySection } from "@/components/PolicySection";

// frob:ticket 01M2H5T11HZP2VXR9KV24Q8RV3
// frob:ticket 01M5VSBWBK5KZ4H6913F333GGC
// frob:doc docs/index.md#landing-and-policy-pages
/** The `/data-policy` route: what the platform stores about a player, why, for how long, and how to have it removed. */
export function DataPolicy() {
  return (
    <Page
      crumbs={[{ label: "Data policy" }]}
      title="Data policy"
      purpose="What this site stores about you, why, and how to get it removed."
    >
      <PolicySection id="stored-data" title="Stored data">
        <p>When you register, the server stores:</p>
        <ul className="m-space-0 list-disc pl-space-24">
          <li>your username and email address;</li>
          <li>a salted hash of your password, never the password itself;</li>
          <li>your role (player or admin), account creation time and ELO rating.</li>
        </ul>
        <p>
          While you play, it stores each match you take part in: the winner, the
          duration, your damage dealt, blocks destroyed, blocks placed and time alive,
          and the ELO change the match caused.
        </p>
        <p>
          Signing in creates a session record holding a hash of your session token and
          its creation, expiry and revocation times. The token itself is kept in
          the HttpOnly session cookie in your browser and is cleared when you log out.
        </p>
        <p>
          Like any web server, the one behind this site may keep standard request logs
          (time, path, status and the address a request came from).
        </p>
      </PolicySection>
      <PolicySection id="purpose" title="Purpose">
        <p>
          Your username identifies you on the leaderboard and in match history. Your
          email address and password hash let you sign in. Match records produce your
          ELO rating, your history and the leaderboard. Session records keep you
          signed in until they expire, 14 days after sign-in by default. Nothing is
          used for advertising, and no data is sold or shared with third parties.
        </p>
      </PolicySection>
      <PolicySection id="deletion" title="Deletion">
        <p>
          There is no self-service account deletion yet. To have your account and its
          match records removed, ask the project maintainers through the repository
          issue tracker. You can change your username, email address and password at
          any time under Settings, and logging out revokes your session.
        </p>
        <p>This is a class project in pre-release; do not rely on it for long-term storage.</p>
      </PolicySection>
    </Page>
  );
}
