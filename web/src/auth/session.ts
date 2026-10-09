import { useSyncExternalStore } from "react";

// frob:doc docs/index.md#session-persistence
/** The signed-in user's session, held in memory only; shape T-0021 populates via login. */
export type StoredSession = {
  token: string;
  userId: string;
  username: string;
  role: string;
};

// frob:invariant INV-006
// The bearer token lives only in this module-scoped variable: never in localStorage,
// sessionStorage or a script-readable cookie, so injected script cannot read it back
// from storage and a reload signs the user out (they re-authenticate via /login).
let current: StoredSession | null = null;
const listeners = new Set<() => void>();

/** Replaces the in-memory session and notifies every subscribed hook. */
function setCurrent(next: StoredSession | null): void {
  current = next;
  listeners.forEach((listener) => listener());
}

/** Registers a change listener for useSyncExternalStore; returns its unsubscribe. */
function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

// frob:doc docs/index.md#session-persistence
/** Keeps the given session in memory (never in web storage) for this page load. */
export function saveSession(session: StoredSession): void {
  setCurrent(session);
}

// frob:doc docs/index.md#session-persistence
/** Returns the in-memory session, or null when signed out or after a reload. */
export function loadSession(): StoredSession | null {
  return current;
}

// frob:doc docs/index.md#session-persistence
/** Drops the in-memory session, e.g. on logout. */
export function clearSession(): void {
  setCurrent(null);
}

// frob:doc docs/index.md#session-persistence
/** React hook exposing the current session, re-rendering on login, logout and profile updates. */
export function useSession(): StoredSession | null {
  return useSyncExternalStore(subscribe, loadSession, loadSession);
}
