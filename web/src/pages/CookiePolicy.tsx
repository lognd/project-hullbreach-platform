import { AppLink } from "@/components/AppLink";
import { COOKIE_NOTICE_KEY } from "@/components/CookieNotice";
import { Page } from "@/components/Page";
import { PolicySection } from "@/components/PolicySection";

// frob:ticket 01M2H5T11HZP2VXR9KV24Q8RV3
// frob:ticket 01M5VSBWBK5KZ4H6913F333GGC
// frob:doc docs/index.md#landing-and-policy-pages
/** The `/cookie-policy` route: names the one session cookie the site sets and the one localStorage flag it keeps. */
export function CookiePolicy() {
  return (
    <Page
      crumbs={[{ label: "Cookie policy" }]}
      title="Cookie policy"
      purpose="This site sets one strictly necessary session cookie and keeps one flag in your browser."
    >
      <PolicySection id="cookies" title="Cookies">
        <p>
          This site sets one cookie, <code className="font-mono">hullbreach_session</code>
          . It is strictly necessary: it keeps you signed in, so a page reload does not
          sign you out. It holds an opaque session token and nothing else, no name or
          email address. It is HttpOnly, so scripts on the page cannot read it, and
          SameSite=Lax. The browser sends it only to this site&apos;s{" "}
          <code className="font-mono">/api</code> paths.
        </p>
        <p>
          The cookie is set when you log in and cleared when you log out. It also
          expires when your session does. The site has no analytics, advertising or
          tracking scripts, and fonts are served from the site itself, not a third
          party.
        </p>
      </PolicySection>
      <PolicySection id="browser-storage" title="Browser storage">
        <p>
          When you dismiss the cookie notice, the site writes one entry to your
          browser&apos;s localStorage, <code className="font-mono">{COOKIE_NOTICE_KEY}</code>
          , with the value <code className="font-mono">dismissed</code>. It exists only
          so the notice does not return on your next visit, and it is never sent to the
          server.
        </p>
        <p>
          Nothing else is kept in browser storage. Clear the entry in your
          browser&apos;s site data settings at any time and the notice will show
          again.
        </p>
      </PolicySection>
      <PolicySection id="more" title="More">
        <p>
          For what the server stores about your account, read the{" "}
          <AppLink
            href="/data-policy"
            className="text-accent underline underline-offset-4 hover:text-ink"
          >
            data policy
          </AppLink>
          .
        </p>
      </PolicySection>
    </Page>
  );
}
