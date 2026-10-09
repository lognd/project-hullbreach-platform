import { createBrowserRouter } from "react-router-dom";
import { App } from "@/App";
import { Register } from "@/pages/Register";
import { History } from "@/pages/History";
import { Login } from "@/pages/Login";
import { Profile } from "@/pages/Profile";
import { Settings } from "@/pages/Settings";

/** Landing route content; a fuller version lands with T-0045/T-0046 in a later milestone. */
function Landing() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-space-8 bg-paper font-base text-ink">
      <h1 className="text-font-size-48 font-semibold tracking-tight">
        Project Hullbreach
      </h1>
      <p className="text-font-size-20 text-muted">Build a ship. Breach a hull.</p>
    </main>
  );
}

/** Fallback route for an unmatched path. */
function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-space-8 bg-paper text-ink">
      <p>Page not found.</p>
    </main>
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
