import { AppLink } from "@/components/AppLink";
import { COOKIE_NOTICE_KEY } from "@/components/CookieNotice";
import { Page } from "@/components/Page";
import { PolicySection } from "@/components/PolicySection";

// frob:ticket 01M2H5T11HZP2VXR9KV24Q8RV3
// frob:doc docs/index.md#landing-and-policy-pages
/** The `/cookie-policy` route: states that the site sets no cookies and names the one localStorage flag it keeps. */
export function CookiePolicy() {
  return (
    <Page
      crumbs={[{ label: "Cookie policy" }]}
      title="Cookie policy"
      purpose="This site sets no cookies. It keeps one flag in your browser."
    >
      <PolicySection id="cookies" title="Cookies">
        <p>
          This site does not set cookies, and it has no analytics, advertising or
          tracking scripts. Fonts are served from the site itself, not a third party.
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
          Your sign-in token is held in memory only, not in cookies or storage, so
          reloading the page signs you out. Clear the entry in your browser&apos;s site
          data settings at any time and the notice will show again.
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
