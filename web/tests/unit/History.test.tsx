import { StrictMode } from "react";
import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fetchMatches } from "@/api/me";
import { saveSession } from "@/auth/session";
import { History } from "@/pages/History";
import { makeMatch, makeMatchPage } from "../fixtures/me";
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

/** The opponents currently listed, in order. */
function listedOpponents(): string[] {
  return screen
    .queryAllByRole("listitem")
    .map((item) => /rival-\d+/.exec(item.textContent ?? "")?.[0] ?? "");
}

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.localStorage.clear();
});

describe("History page", () => {
  // frob:tests web/src/pages/History.tsx::History kind="unit"
  // frob:tests web/src/components/MatchItem.tsx::MatchItem kind="unit"
  it("lists the first page newest first with details and a Load more control", async () => {
    signIn();
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(makeMatchPage(0, 3, 5)));
    vi.stubGlobal("fetch", fetchMock);
    render(<History />);

    expect(await screen.findByText("rival-0")).toBeInTheDocument();
    expect(listedOpponents()).toEqual(["rival-0", "rival-1", "rival-2"]);
    const first = screen.getAllByRole("listitem")[0];
    expect(within(first).getByText("Win")).toBeInTheDocument();
    expect(first).toHaveTextContent("1200 -> 1212");
    expect(first).toHaveTextContent("2026-10-28");
    expect(first).toHaveTextContent("5:00");
    expect(first).toHaveTextContent("damage dealt 900");
    expect(first).toHaveTextContent("hull breaches 3");
    expect(screen.getAllByRole("listitem")[1]).toHaveTextContent("Loss");
    expect(screen.getByRole("button", { name: "Load more" })).toBeEnabled();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/me/matches",
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer tok-1" }),
      }),
    );
  });

  // frob:tests web/src/pages/History.tsx::History kind="unit"
  it("appends the next page on Load more and drops the control on the last page", async () => {
    signIn();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(makeMatchPage(0, 3, 5)))
      .mockResolvedValueOnce(jsonResponse(makeMatchPage(3, 3, 5)));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<History />);

    await user.click(await screen.findByRole("button", { name: "Load more" }));

    expect(await screen.findByText("rival-4")).toBeInTheDocument();
    expect(listedOpponents()).toEqual([
      "rival-0",
      "rival-1",
      "rival-2",
      "rival-3",
      "rival-4",
    ]);
    expect(fetchMock.mock.calls[1][0]).toBe("/api/v1/me/matches?cursor=cursor-3");
    expect(screen.queryByRole("button", { name: /load more/i })).not.toBeInTheDocument();
  });

  // frob:tests web/src/pages/History.tsx::History kind="unit"
  it("disables Load more while a page is in flight so a double click sends one request", async () => {
    signIn();
    let release: (response: Response) => void = () => {};
    const pending = new Promise<Response>((resolve) => {
      release = resolve;
    });
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(makeMatchPage(0, 3, 5)))
      .mockReturnValueOnce(pending);
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<History />);

    const button = await screen.findByRole("button", { name: "Load more" });
    await user.click(button);
    await user.click(button);

    expect(button).toBeDisabled();
    expect(fetchMock).toHaveBeenCalledTimes(2);
    release(jsonResponse(makeMatchPage(3, 3, 5)));
    expect(await screen.findByText("rival-4")).toBeInTheDocument();
  });

  // frob:tests web/src/pages/History.tsx::History kind="unit"
  it("keeps the loaded matches and offers a retry when Load more fails", async () => {
    signIn();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(makeMatchPage(0, 3, 5)))
      .mockResolvedValueOnce(jsonResponse({ detail: "service unavailable" }, 503))
      .mockResolvedValueOnce(jsonResponse(makeMatchPage(3, 3, 5)));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<History />);

    await user.click(await screen.findByRole("button", { name: "Load more" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("service unavailable");
    expect(listedOpponents()).toEqual(["rival-0", "rival-1", "rival-2"]);

    await user.click(screen.getByRole("button", { name: "Load more" }));

    expect(await screen.findByText("rival-4")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(fetchMock.mock.calls[2][0]).toBe("/api/v1/me/matches?cursor=cursor-3");
  });

  // frob:tests web/src/pages/History.tsx::History kind="unit"
  it("offers Try again when the first page fails, then loads it", async () => {
    signIn();
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError("offline"))
      .mockResolvedValueOnce(jsonResponse(makeMatchPage(0, 3, 3)));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<History />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/something went wrong/i);
    await user.click(screen.getByRole("button", { name: "Try again" }));

    expect(await screen.findByText("rival-0")).toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  // frob:tests web/src/pages/History.tsx::History kind="unit"
  it("shows an empty state for a player with no matches", async () => {
    signIn();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ items: [], next_cursor: null })),
    );
    render(<History />);

    expect(await screen.findByText("No matches yet.")).toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  // frob:tests web/src/pages/History.tsx::History kind="unit"
  it("lists each match once under StrictMode's double-run effects", async () => {
    signIn();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(() => Promise.resolve(jsonResponse(makeMatchPage(0, 3, 3)))),
    );
    render(
      <StrictMode>
        <History />
      </StrictMode>,
    );

    await screen.findByText("rival-0");
    expect(listedOpponents()).toEqual(["rival-0", "rival-1", "rival-2"]);
  });

  // frob:tests web/src/pages/History.tsx::History kind="unit"
  // frob:tests web/src/components/SignInPrompt.tsx::SignInPrompt kind="unit"
  it("asks a signed-out visitor to log in and makes no request", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    render(<History />);

    expect(screen.getByRole("link", { name: /log in/i })).toHaveAttribute(
      "href",
      "/login",
    );
    expect(fetchMock).not.toHaveBeenCalled();
  });

  // frob:tests web/src/pages/History.tsx::History kind="unit"
  it("lays out for a 400px phone width without horizontal overflow", async () => {
    // jsdom cannot measure layout; assert the contract (see Profile.test.tsx).
    signIn();
    const longName = "x".repeat(60);
    const page = {
      items: [{ ...makeMatch(0), opponent: longName }],
      next_cursor: "cursor-1",
    };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(page)));
    const { container } = render(<History />);

    await screen.findByText(longName);
    expect(overflowRisks(container, 400)).toEqual([]);
    expect(screen.getByText(longName)).toHaveClass("wrap-anywhere");
  });
});

describe("fetchMatches", () => {
  // frob:tests web/src/api/me.ts::fetchMatches kind="unit"
  it("encodes the cursor into the query string", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(makeMatchPage(0, 1, 1)));
    vi.stubGlobal("fetch", fetchMock);

    await fetchMatches("tok-1", "a b&c");

    expect(fetchMock.mock.calls[0][0]).toBe("/api/v1/me/matches?cursor=a%20b%26c");
  });
});
