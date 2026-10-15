import { useSyncExternalStore } from "react";

// frob:doc docs/index.md#routing-and-page-shell
/** Moves to `href` without a page load (history push plus the popstate the data router listens for), so the in-memory session (INV-006) survives; works with no router mounted too. */
export function navigate(href: string): void {
  window.history.pushState({}, "", href);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

/** Calls `onChange` on every history move; navigate() dispatches popstate, so in-app moves count too. */
function subscribe(onChange: () => void): () => void {
  window.addEventListener("popstate", onChange);
  return () => window.removeEventListener("popstate", onChange);
}

// frob:doc docs/index.md#routing-and-page-shell
/** The current path, re-rendering on navigation; lets the header mark the active link without needing a router context. */
export function usePathname(): string {
  return useSyncExternalStore(subscribe, () => window.location.pathname);
}
