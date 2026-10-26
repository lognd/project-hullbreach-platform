import { useState } from "react";
import { AppLink } from "@/components/AppLink";
import { Button } from "@/components/Button";
import { Notice } from "@/components/Notice";

/** localStorage key holding the dismissal flag; named on the cookie policy page. */
export const COOKIE_NOTICE_KEY = "hullbreach.cookie-notice";

/** Value stored under COOKIE_NOTICE_KEY once the notice is dismissed. */
const DISMISSED = "dismissed";

/** True when the visitor already dismissed the notice; unreadable storage counts as not dismissed. */
function wasDismissed(): boolean {
  try {
    return window.localStorage.getItem(COOKIE_NOTICE_KEY) === DISMISSED;
  } catch {
    return false;
  }
}

/** Remembers the dismissal; storage that refuses the write just means the notice returns next visit. */
function rememberDismissal(): void {
  try {
    window.localStorage.setItem(COOKIE_NOTICE_KEY, DISMISSED);
  } catch {
    // Storage blocked (private mode or quota): hide for this page load only.
  }
}

// frob:ticket 01M2H5T11GEGRR23QSDXER9PXR
// frob:doc docs/index.md#landing-and-policy-pages
/** A dismissible strip stating the site sets no cookies and keeps one localStorage flag; hidden for good once dismissed. */
export function CookieNotice() {
  const [hidden, setHidden] = useState(wasDismissed);
  if (hidden) {
    return null;
  }
  return (
    <section
      aria-label="Cookie notice"
      className="px-space-16 pt-space-16 sm:px-space-24"
    >
      <Notice tone="info">
        <p className="m-space-0 max-w-[40rem]">
          This site sets no cookies. Dismissing this notice stores one flag in your
          browser.{" "}
          <AppLink
            href="/cookie-policy"
            className="text-accent underline underline-offset-4 hover:text-ink"
          >
            Cookie policy
          </AppLink>
        </p>
        <Button
          onClick={() => {
            rememberDismissal();
            setHidden(true);
          }}
        >
          Dismiss
        </Button>
      </Notice>
    </section>
  );
}
