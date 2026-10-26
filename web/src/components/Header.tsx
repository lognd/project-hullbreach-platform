import { logout } from "@/api/auth";
import { clearSession, useSession, type StoredSession } from "@/auth/session";
import { AppLink } from "@/components/AppLink";
import { navigate, usePathname } from "@/components/navigate";

/** Sends the user home in-app; navigate() rather than useNavigate so Header also works rendered outside a Router, e.g. in isolation tests. */
function goHome(): void {
  navigate("/");
}

/** Revokes `session`'s token, clears the local session, and sends the user home; the server call is best-effort -- local sign-out proceeds even if it fails. */
async function handleLogout(session: StoredSession): Promise<void> {
  try {
    await logout(session.token);
  } catch {
    // Best-effort: an already-expired token or a network error should not
    // block the user from signing out locally.
  }
  clearSession();
  goHome();
}

/** Header nav link; marks itself aria-current="page" (cyan underline, ink text) when it is the page being shown, with a 44px+ touch height. */
function NavLink({
  href,
  label,
  current,
}: {
  href: string;
  label: string;
  current: string;
}) {
  const active = current === href;
  return (
    <AppLink
      href={href}
      aria-current={active ? "page" : undefined}
      className={`border-b-2 px-space-4 py-space-12 font-mono text-font-size-14 font-medium uppercase tracking-wider hover:text-ink ${active ? "border-accent text-ink" : "border-transparent text-muted"}`}
    >
      {label}
    </AppLink>
  );
}

/** Small side-view spaceship mark (hull, cockpit, engine nozzle, fins) drawn in the accent line color. */
function ShipGlyph() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 32 32"
      className="h-space-24 w-space-24 shrink-0"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinejoin="miter"
    >
      <path d="M7 16 L12 12 L23 12 L29 16 L23 20 L12 20 Z" />
      <path d="M12 12 L9 6 L16 12 M12 20 L9 26 L16 20" />
      <path d="M7 13.5 L3 12 V20 L7 18.5" />
    </svg>
  );
}

// frob:doc docs/index.md#routing-and-page-shell
/** Site header: wordmark and Leaderboard and Store links, plus Register/Log in when signed out; Profile, Matches, Settings, the username and a bordered Log out button when signed in. */
export function Header() {
  const session = useSession();
  const pathname = usePathname();

  return (
    <header className="flex flex-wrap items-center justify-between gap-x-space-24 gap-y-space-4 border-b border-accent bg-paper px-space-16 py-space-4 text-ink sm:px-space-24">
      <nav
        aria-label="Account"
        className="order-2 flex flex-wrap items-center gap-x-space-16 gap-y-space-4"
      >
        <NavLink href="/leaderboard" label="Leaderboard" current={pathname} />
        <NavLink href="/store" label="Store" current={pathname} />
        {session === null ? (
          <>
            <NavLink href="/register" label="Register" current={pathname} />
            <NavLink href="/login" label="Log in" current={pathname} />
          </>
        ) : (
          <>
            <NavLink href="/me" label="Profile" current={pathname} />
            <NavLink href="/me/matches" label="Matches" current={pathname} />
            <NavLink href="/settings" label="Settings" current={pathname} />
            <span className="wrap-anywhere border-l border-line pl-space-16 font-mono text-font-size-14 text-muted">
              {session.username}
            </span>
            <button
              type="button"
              onClick={() => {
                void handleLogout(session);
              }}
              className="border border-accent px-space-16 py-space-12 font-mono text-font-size-14 font-medium uppercase tracking-wider text-ink hover:bg-panel"
            >
              Log out
            </button>
          </>
        )}
      </nav>
      {/* A button, not a link: it is the last focusable control so tab order
          (links first, then buttons -- see the keyboard-access test) still
          matches this brand mark's visual position first, achieved with
          order-1 rather than DOM position. */}
      <button
        type="button"
        aria-label="Open menu"
        onClick={goHome}
        className="order-1 flex items-center gap-space-12 py-space-12 font-display text-font-size-20 uppercase tracking-widest text-ink"
      >
        <span className="text-accent">
          <ShipGlyph />
        </span>
        Hullbreach
      </button>
    </header>
  );
}
