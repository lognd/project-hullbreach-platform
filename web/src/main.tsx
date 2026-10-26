import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { restoreSession } from "@/auth/session";
import { router } from "@/router";
import "@fontsource/audiowide/400.css";
import "@fontsource/ibm-plex-mono/400.css";
import "@fontsource/ibm-plex-mono/500.css";
import "@fontsource/ibm-plex-mono/600.css";
import "@fontsource/ibm-plex-sans/400.css";
import "@fontsource/ibm-plex-sans/500.css";
import "@/index.css";

const root = document.getElementById("root");
if (root === null) {
  throw new Error("#root element not found");
}

// Restore the cookie session before first paint so a reload does not flash signed-out.
void restoreSession().then(() => {
  createRoot(root).render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>,
  );
});
