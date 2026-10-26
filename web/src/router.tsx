import { createBrowserRouter } from "react-router-dom";
import { App } from "@/App";
import { Register } from "@/pages/Register";
import { History } from "@/pages/History";
import { Login } from "@/pages/Login";
import { Profile } from "@/pages/Profile";
import { Settings } from "@/pages/Settings";
import { useSession } from "@/auth/session";
import { AppLink } from "@/components/AppLink";
import { ButtonLink } from "@/components/Button";
import { HullReadout } from "@/components/HullReadout";
import { Page } from "@/components/Page";

/** The four beats of a match, numbered down the landing page: what you do, in the order you do it. */
const LOOP = [
  ["01", "Build", "Assemble your ship block by block: hull, thrusters, weapons."],
  ["02", "Fly", "Real gravity, real momentum. Mass you add is mass you have to move."],
  [
    "03",
    "Breach",
    "Hits load the hull block by block. Overload one and it breaks open.",
  ],
  ["04", "Rank", "Every match moves your ELO and lands in your match history."],
] as const;

/** Landing route content; a fuller version lands with T-0045/T-0046 in a later milestone. */
function Landing() {
  const session = useSession();
  return (
    <main className="flex w-full flex-1 flex-col bg-paper text-ink">
      <div className="mx-auto grid w-full max-w-[72rem] items-start gap-space-48 px-space-16 py-space-48 sm:px-space-24 lg:grid-cols-2 lg:py-space-64">
        <div className="flex flex-col gap-space-24">
          <div className="flex flex-col gap-space-12">
            <h1 className="font-display text-font-size-48 uppercase leading-none tracking-wider">
              Project Hullbreach
            </h1>
            <h2 className="font-display text-font-size-24 uppercase leading-tight tracking-wider text-accent">
              Build. Breach. Claim the void.
            </h2>
          </div>
          <p className="max-w-[32rem] text-font-size-20 text-muted">
            Build a spaceship one block at a time. Fly it under real gravity. Break the
            enemy&apos;s hull before it breaks yours.
          </p>
          <div className="flex flex-wrap gap-space-12">
            {session === null ? (
              <>
                <ButtonLink href="/login" variant="primary">
                  Log in
                </ButtonLink>
                <ButtonLink href="/register">Create account</ButtonLink>
              </>
            ) : (
              <>
                <ButtonLink href="/me" variant="primary">
                  Profile
                </ButtonLink>
                <ButtonLink href="/me/matches">Match history</ButtonLink>
              </>
            )}
          </div>
          <ol className="grid gap-space-8 sm:grid-cols-2">
            {LOOP.map(([step, name, line]) => (
              <li
                key={step}
                className="flex flex-col gap-space-4 border border-line bg-panel px-space-16 py-space-12"
              >
                <span className="font-mono text-font-size-12 uppercase tracking-widest text-accent">
                  {step} {name}
                </span>
                <span className="text-font-size-14 text-muted">{line}</span>
              </li>
            ))}
          </ol>
        </div>
        <HullReadout />
      </div>
    </main>
  );
}

/** Fallback route for an unmatched path. */
function NotFound() {
  return (
    <Page
      crumbs={[{ label: "404" }]}
      title="Page not found."
      purpose="That address does not lead anywhere in the app."
    >
      <p className="text-font-size-16 text-muted">
        Check the address, or{" "}
        <AppLink
          href="/"
          className="font-medium text-accent underline underline-offset-4 hover:text-ink"
        >
          go back to the start
        </AppLink>
      </p>
    </Page>
  );
}

// frob:doc docs/index.md#routing-and-page-shell
/** The app's data router: App is the page shell, its children are routed under the Outlet. */
export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Landing /> },
      { path: "register", element: <Register /> },
      { path: "login", element: <Login /> },
      { path: "me", element: <Profile /> },
      { path: "me/matches", element: <History /> },
      { path: "settings", element: <Settings /> },
      // Each queued page is one more route here plus a pages/<Name>.tsx and
      // a tests/unit/<Name>.test.tsx; copy pages/Login.tsx. Add this file to
      // the ticket's scope first (`frob ticket scope T-#### --add`).
      // frob:todo 01M2H5T11EWXN4QEQ0QET8ZC6Y index route -> pages/Landing.tsx replaces the stub above
      // frob:todo 01M2H5T11HZP2VXR9KV24Q8RV3 path data-policy -> pages/DataPolicy.tsx (Footer already links it)
      // frob:todo 01M2H5T11ZXF08TGJ9RWXBB2TD path leaderboard -> pages/Leaderboard.tsx
      // frob:todo 01M2H5T1242JFMB5A03JSDP5KP path store -> pages/Store.tsx
      // frob:todo 01M2H5T12E0JWYSBMM6HZ09J6Q path admin/* -> pages/admin/, gated on role is admin
      { path: "*", element: <NotFound /> },
    ],
  },
]);
