import { useSyncExternalStore } from "react";
import { fetchMe } from "@/api/me";

// frob:doc docs/index.md#session-persistence
/** The signed-in user's session, held in memory only; token is "" when restored from the HttpOnly cookie. */
export type StoredSession = {
  token: string;
  userId: string;
  username: string;
  role: string;
};

// frob:invariant INV-006
// The bearer token lives only in this module-scoped variable: never in localStorage,
// sessionStorage or a script-readable cookie, so injected script cannot read it back.
// A reload keeps the user signed in through the server's HttpOnly session cookie
// (restoreSession below), which page script cannot read either.
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

/** Restore-on-load budget: short so a dead server delays first paint only briefly. */
const RESTORE_TIMEOUT_MS = 3_000;

// frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
// frob:doc docs/index.md#session-persistence
/** Restores the session after a reload from the HttpOnly cookie via GET /api/v1/me; resolves true when signed in, false (staying signed out) on any failure. */
export async function restoreSession(): Promise<boolean> {
  try {
    const me = await fetchMe("", RESTORE_TIMEOUT_MS);
    saveSession({ token: "", userId: me.id, username: me.username, role: me.role });
    return true;
  } catch {
    return false;
  }
}
