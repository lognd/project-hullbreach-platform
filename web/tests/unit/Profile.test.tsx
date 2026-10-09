import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fetchMe } from "@/api/me";
import { register, login } from "@/api/auth";
import { saveSession } from "@/auth/session";
import { Profile } from "@/pages/Profile";
import { makeMatch, meFixture } from "../fixtures/me";
import { overflowRisks } from "../support/layout";

/** A JSON Response, as the server would send it. */
function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

/** Persists a signed-in session so the page has a token to send. */
function signIn(): void {
  saveSession({ token: "tok-1", userId: "user-1", username: "flagship", role: "player" });
}

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.localStorage.clear();
});

describe("Profile page", () => {
  // frob:tests web/src/pages/Profile.tsx::Profile kind="unit"
  // frob:tests web/src/components/MatchItem.tsx::MatchItem kind="unit"
  // frob:tests web/src/api/auth.ts::bearerHeaders kind="unit"
  // frob:tests web/src/api/auth.ts::requestJson kind="unit"
  it("shows username, rating, currency, owned skins and the last five matches", async () => {
    signIn();
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(meFixture));
    vi.stubGlobal("fetch", fetchMock);
    render(<Profile />);

    expect(await screen.findByRole("heading", { name: "flagship" })).toBeInTheDocument();
    expect(screen.getByText("1236")).toBeInTheDocument();
    expect(screen.getByText("450")).toBeInTheDocument();
    expect(screen.getByText("Ember Hull")).toBeInTheDocument();
    expect(screen.getByText("Frost Plating")).toBeInTheDocument();
    const matches = screen.getByRole("heading", { name: "Recent matches" }).closest("section");
    expect(within(matches as HTMLElement).getAllByRole("listitem")).toHaveLength(5);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/me",
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer tok-1" }),
      }),
    );
  });

  // frob:tests web/src/pages/Profile.tsx::Profile kind="unit"
  it("caps the recent matches at five even if the server sends more", async () => {
    signIn();
    const many = { ...meFixture, recent_matches: [0, 1, 2, 3, 4, 5, 6].map(makeMatch) };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(many)));
    render(<Profile />);

    const section = (await screen.findByText("Recent matches")).closest("section");
    expect(within(section as HTMLElement).getAllByRole("listitem")).toHaveLength(5);
  });

  // frob:tests web/src/pages/Profile.tsx::Profile kind="unit"
  it("shows empty states for a player with no skins or matches", async () => {
    signIn();
    const empty = { ...meFixture, inventory: [], recent_matches: [] };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(empty)));
    render(<Profile />);

    expect(await screen.findByText("No skins yet.")).toBeInTheDocument();
    expect(screen.getByText("No matches yet.")).toBeInTheDocument();
  });

  // frob:tests web/src/pages/Profile.tsx::Profile kind="unit"
  it("asks a signed-out visitor to log in and makes no request", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    render(<Profile />);

    expect(screen.getByRole("link", { name: /log in/i })).toHaveAttribute(
      "href",
      "/login",
    );
    expect(fetchMock).not.toHaveBeenCalled();
  });

  // frob:tests web/src/pages/Profile.tsx::Profile kind="unit"
  it("shows the server's message when the request is rejected", async () => {
    signIn();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ detail: "invalid or expired token" }, 401)),
    );
    render(<Profile />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "invalid or expired token",
    );
  });

  // frob:tests web/src/pages/Profile.tsx::Profile kind="unit"
  it("shows a generic message when the network fails", async () => {
    signIn();
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));
    render(<Profile />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/something went wrong/i);
  });

  // frob:tests web/src/pages/Profile.tsx::Profile kind="unit"
  it("lays out for a 400px phone width without horizontal overflow", async () => {
    // jsdom has no layout engine, so scrollWidth cannot be measured; instead assert
    // the layout contract: no fixed width wider than the viewport, no unwrappable
    // text, and every user-supplied string (username, skin, opponent) may break.
    const longName = "x".repeat(60);
    signIn();
    const wide = {
      ...meFixture,
      username: longName,
      inventory: [{ id: "item-9", slug: "long", name: longName }],
      recent_matches: [{ ...makeMatch(0), opponent: longName }],
    };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(wide)));
    const { container } = render(<Profile />);

    await screen.findByRole("heading", { name: longName });
    expect(overflowRisks(container, 400)).toEqual([]);
    for (const element of screen.getAllByText(longName)) {
      expect(element).toHaveClass("wrap-anywhere");
    }
  });
});

describe("overflowRisks", () => {
  // frob:tests web/tests/support/layout.ts::overflowRisks kind="unit"
  it("flags a fixed width wider than the viewport and unwrappable text", () => {
    const { container } = render(
      <div className="w-[32rem]">
        <p className="whitespace-nowrap">text</p>
        <p className="w-[20rem]">fits</p>
      </div>,
    );

    expect(overflowRisks(container, 400)).toEqual([
      "div: w-[32rem] (512px)",
      "p: whitespace-nowrap",
    ]);
  });
});

describe("fetchMe", () => {
  // frob:tests web/src/api/me.ts::fetchMe kind="unit"
  it("rejects with the server's detail on a non-2xx response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ detail: "invalid or expired token" }, 401)),
    );

    await expect(fetchMe("bad")).rejects.toMatchObject({
      status: 401,
      detail: "invalid or expired token",
    });
  });
});

describe("Profile against the live server", () => {
  // Known tracked gap: GET /api/v1/me (T-0031) is not implemented yet. This test
  // exercises the real client against a running dev server (register, log in,
  // fetchMe), so it fails while the endpoint is missing or no server runs. When
  // T-0031 lands it passes, `it.fails` turns red, and that is the cue to drop
  // `.fails` and the marker below.
  // frob:todo 01M2H5T10ZV4EV17ZMHTQ455KJ drop it.fails once GET /api/v1/me is live
  // frob:tests web/src/api/me.ts::fetchMe kind="integration"
  it.fails("returns the profile contract from the live GET /api/v1/me", async () => {
    const realFetch = globalThis.fetch;
    vi.stubGlobal("fetch", (path: string, init?: RequestInit) =>
      realFetch(`http://127.0.0.1:8000${path}`, init),
    );
    const suffix = Math.random().toString(36).slice(2, 10);
    const credentials = {
      username: `vitest-${suffix}`,
      email: `vitest-${suffix}@example.com`,
      password: "correct-horse-battery",
    };
    await register(credentials);
    const { token } = await login({
      username: credentials.username,
      password: credentials.password,
    });

    const me = await fetchMe(token);

    expect(me.username).toBe(credentials.username);
    expect(Array.isArray(me.inventory)).toBe(true);
    expect(Array.isArray(me.recent_matches)).toBe(true);
  });
});
