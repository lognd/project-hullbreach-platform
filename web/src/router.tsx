import { createBrowserRouter } from "react-router-dom";
import { App } from "@/App";
import { CookiePolicy } from "@/pages/CookiePolicy";
import { DataPolicy } from "@/pages/DataPolicy";
import { Landing } from "@/pages/Landing";
import { Register } from "@/pages/Register";
import { History } from "@/pages/History";
import { Leaderboard } from "@/pages/Leaderboard";
import { Login } from "@/pages/Login";
import { Profile } from "@/pages/Profile";
import { Settings } from "@/pages/Settings";
import { Store } from "@/pages/Store";
import { AppLink } from "@/components/AppLink";
import { Page } from "@/components/Page";

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
      // frob:ticket 01M2H5T11EWXN4QEQ0QET8ZC6Y
      { index: true, element: <Landing /> },
      { path: "register", element: <Register /> },
      { path: "login", element: <Login /> },
      { path: "me", element: <Profile /> },
      { path: "me/matches", element: <History /> },
      { path: "leaderboard", element: <Leaderboard /> },
      { path: "settings", element: <Settings /> },
      // frob:ticket 01M2H5T11HZP2VXR9KV24Q8RV3
      { path: "data-policy", element: <DataPolicy /> },
      { path: "cookie-policy", element: <CookiePolicy /> },
      // Each queued page is one more route here plus a pages/<Name>.tsx and
      // a tests/unit/<Name>.test.tsx; copy pages/Login.tsx. Add this file to
      // the ticket's scope first (`frob ticket scope T-#### --add`).
      // frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
      { path: "store", element: <Store /> },
      // frob:todo 01M2H5T12E0JWYSBMM6HZ09J6Q path admin/* -> pages/admin/, gated on role is admin
      { path: "*", element: <NotFound /> },
    ],
  },
]);
