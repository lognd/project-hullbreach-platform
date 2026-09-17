import { createBrowserRouter } from "react-router-dom";
import { App } from "@/App";
import { Register } from "@/pages/Register";

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

/** Login route content; the real form lands with T-0021 in web/src/pages/Login.tsx. */
function Login() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-space-8 bg-paper text-ink">
      <h1 className="text-font-size-32 font-semibold">Log in</h1>
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

// frob:tests web/tests/unit/Header.test.tsx kind="unit"
// frob:doc docs/index.md#routing-and-page-shell
// frob:waive REF002 reason="single-anchor by design: wired only from web/src/main.tsx \
// (the app's one entry point) plus this one doc anchor -- a second consumer would be \
// an unused, invented import"
/** The app's data router: App is the page shell, its children are routed under the Outlet. */
export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Landing /> },
      { path: "register", element: <Register /> },
      { path: "login", element: <Login /> },
      { path: "*", element: <NotFound /> },
    ],
  },
]);
