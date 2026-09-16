import { useSession } from "@/auth/session";

// frob:todo T-0024
/** Placeholder logout handler; T-0024 wires this to api/auth.ts's logout(), clearSession(), and a navigate to "/". */
function handleLogoutPlaceholder(): void {
  // Intentionally empty: real behavior (revoke token, clear session, redirect
  // home) lands with T-0024. This exists only so the control is a real,
  // focusable, Enter-activatable <button> per T-0044's keyboard-access
  // acceptance criterion.
}

/** Sends the user home; a plain assignment (not useNavigate) so Header also works rendered outside a Router, e.g. in isolation tests. */
function goHome(): void {
  window.location.assign("/");
}

// frob:tests web/tests/unit/Header.test.tsx kind="unit"
// frob:doc docs/index.md#routing-and-page-shell
/** Site header: brand plus Register/Login links when signed out, or the username and a Log out control when signed in. */
export function Header() {
  const session = useSession();

  return (
    <header className="flex items-center justify-between gap-space-16 bg-panel px-space-24 py-space-16 text-ink">
      <nav className="order-2 flex items-center gap-space-16">
        {session === null ? (
          <>
            <a href="/register" className="text-font-size-16">
              Register
            </a>
            <a href="/login" className="text-font-size-16">
              Log in
            </a>
          </>
        ) : (
          <>
            <span className="text-font-size-16 text-muted">{session.username}</span>
            <button
              type="button"
              onClick={handleLogoutPlaceholder}
              className="text-font-size-16"
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
        className="order-1 text-font-size-20 font-semibold tracking-tight"
      >
        Hullbreach
      </button>
    </header>
  );
}
