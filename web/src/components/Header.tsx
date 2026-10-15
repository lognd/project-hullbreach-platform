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

/** Header nav link; marks itself aria-current="page" (accent underline) when it is the page being shown. */
function NavLink({ href, label, current }: { href: string; label: string; current: string }) {
  const active = current === href;
  return (
    <AppLink
      href={href}
      aria-current={active ? "page" : undefined}
      className={`border-b-2 py-space-4 text-font-size-14 font-medium hover:text-ink ${active ? "border-accent text-ink" : "border-paper text-muted"}`}
    >
      {label}
    </AppLink>
  );
}

// frob:doc docs/index.md#routing-and-page-shell
/** Site header: brand plus Register/Log in when signed out; Profile, Matches and Settings links, the username and Log out when signed in. */
export function Header() {
  const session = useSession();
  const pathname = usePathname();

  return (
    <header className="flex flex-wrap items-center justify-between gap-x-space-24 gap-y-space-8 border-b border-line bg-paper px-space-16 py-space-12 text-ink sm:px-space-24">
      <nav aria-label="Account" className="order-2 flex flex-wrap items-center gap-x-space-16 gap-y-space-8">
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
              className="py-space-4 text-font-size-14 font-medium text-muted hover:text-ink"
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
        onClick={goHome}
        className="order-1 flex items-center gap-space-8 font-mono text-font-size-16 font-bold uppercase tracking-widest text-ink"
      >
        <span aria-hidden="true" className="block h-space-12 w-space-12 bg-accent" />
        Hullbreach
      </button>
    </header>
  );
}
