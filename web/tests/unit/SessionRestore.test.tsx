// Cookie session restore and the fetch timeout (~6TZCHZ0, ~R5PHHZC).
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, apiFetch, bearerHeaders, logout } from "@/api/auth";
import { loadSession, restoreSession } from "@/auth/session";

const ME = {
  id: "u-1",
  username: "pilot",
  email: "pilot@example.com",
  role: "player",
  currency: 0,
  rating: 1200,
  created_at: "2026-01-01T00:00:00Z",
  inventory: [],
  recent_matches: [],
};

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("session restore and request hardening", () => {
  beforeEach(() => {
    vi.useRealTimers();
  });
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  // frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
  // frob:tests web/src/auth/session.ts::restoreSession kind="unit"
  it("restores the session from the cookie via GET /api/v1/me with no token in storage", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, ME));
    vi.stubGlobal("fetch", fetchMock);

    await expect(restoreSession()).resolves.toBe(true);

    expect(loadSession()).toEqual({
      token: "",
      userId: "u-1",
      username: "pilot",
      role: "player",
    });
    const [path, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(path).toBe("/api/v1/me");
    expect(init.credentials).toBe("include");
    expect(init.headers).not.toHaveProperty("Authorization");
    expect(window.localStorage.length).toBe(0);
    expect(window.sessionStorage.length).toBe(0);
  });

  // frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
  // frob:tests web/src/auth/session.ts::restoreSession kind="unit"
  it("stays signed out when the server answers 401 or is unreachable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse(401, { detail: "not authenticated" })),
    );
    await expect(restoreSession()).resolves.toBe(false);
    expect(loadSession()).toBeNull();

    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));
    await expect(restoreSession()).resolves.toBe(false);
    expect(loadSession()).toBeNull();
  });

  // frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
  // frob:tests web/src/api/auth.ts::apiFetch kind="unit"
  it("sends credentials and the CSRF header on every request", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);

    await logout("tok-1");

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.credentials).toBe("include");
    expect(init.headers).toMatchObject({
      Authorization: "Bearer tok-1",
      "X-Hullbreach-Web": "1",
    });
    expect(bearerHeaders("")).toEqual({});
  });

  // frob:ticket 01M2KR6R362BWF543KBR5PHHZC
  // frob:tests web/src/api/auth.ts::apiFetch kind="unit"
  it("aborts a hung request after the timeout with an ApiError", async () => {
    vi.useFakeTimers();
    vi.stubGlobal(
      "fetch",
      vi.fn(
        (_path: string, init: RequestInit) =>
          new Promise((_resolve, reject) => {
            init.signal?.addEventListener("abort", () => {
              reject(new DOMException("aborted", "AbortError"));
            });
          }),
      ),
    );

    const pending = apiFetch("/api/v1/me", {}, 50);
    const assertion = expect(pending).rejects.toMatchObject({
      status: 0,
      detail: "request timed out",
    });
    await vi.advanceTimersByTimeAsync(60);
    await assertion;
    await expect(pending).rejects.toBeInstanceOf(ApiError);
  });
});
