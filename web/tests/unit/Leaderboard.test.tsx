import { StrictMode } from "react";
import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { clearSession, saveSession } from "@/auth/session";
import { fetchLeaderboard } from "@/api/leaderboard";
import { Leaderboard } from "@/pages/Leaderboard";
import { makeBoard, makeEntry } from "../fixtures/leaderboard";
import { overflowRisks } from "../support/layout";

/** A JSON Response, as the server would send it. */
function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

/** Signs in as the player behind `pilot-<rank>`. */
function signInAs(rank: number): void {
  saveSession({
    token: "tok-1",
    userId: `user-${rank}`,
    username: `pilot-${rank}`,
    role: "player",
  });
}

beforeEach(() => {
  clearSession();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  clearSession();
});

describe("Leaderboard page", () => {
  // frob:tests web/src/pages/Leaderboard.tsx::Leaderboard kind="unit"
  it("lists the players by rank with ELO and matches, with no token for a visitor", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(makeBoard(3, 3)));
    vi.stubGlobal("fetch", fetchMock);
    render(<Leaderboard />);

    expect(await screen.findByText("pilot-1")).toBeInTheDocument();
    const rows = screen.getAllByRole("listitem");
    expect(rows).toHaveLength(3);
    expect(rows[0]).toHaveTextContent("pilot-1");
    expect(rows[0]).toHaveTextContent("1490");
    expect(rows[2]).toHaveTextContent("pilot-3");
    expect(screen.getByText("3 shown of 3 ranked")).toBeInTheDocument();
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(init.credentials).toBe("include");
    expect(init.headers).not.toHaveProperty("Authorization");
    expect(fetchMock.mock.calls[0]?.[0]).toBe("/api/v1/leaderboard");
  });

  // frob:tests web/src/pages/Leaderboard.tsx::Leaderboard kind="unit"
  it("highlights the signed-in player's row and sends their token", async () => {
    signInAs(2);
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse(makeBoard(3, 3, makeEntry(2))));
    vi.stubGlobal("fetch", fetchMock);
    render(<Leaderboard />);

    await screen.findByText("pilot-1");
    const rows = screen.getAllByRole("listitem");
    expect(rows).toHaveLength(3);
    expect(rows[1]).toHaveAttribute("aria-current", "true");
    expect(within(rows[1]).getByText("You")).toBeInTheDocument();
    expect(rows[0]).not.toHaveAttribute("aria-current");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/leaderboard",
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer tok-1" }),
      }),
    );
  });

  // frob:tests web/src/pages/Leaderboard.tsx::Leaderboard kind="unit"
  it("shows the player's own rank below the list when they are outside the top", async () => {
    signInAs(340);
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse(makeBoard(3, 340, makeEntry(340)))),
    );
    render(<Leaderboard />);

    await screen.findByText("pilot-1");
    const rows = screen.getAllByRole("listitem");
    expect(rows).toHaveLength(4);
    expect(rows[3]).toHaveTextContent("340");
    expect(rows[3]).toHaveTextContent("pilot-340");
    expect(rows[3]).toHaveAttribute("aria-current", "true");
    expect(screen.getByText("Your rank")).toBeInTheDocument();
    expect(screen.getByText("3 shown of 340 ranked")).toBeInTheDocument();
  });

  // frob:tests web/src/pages/Leaderboard.tsx::Leaderboard kind="unit"
  it("shows a loading status and skeleton rows until the board arrives", async () => {
    let release: (response: Response) => void = () => {};
    vi.stubGlobal(
      "fetch",
      vi.fn().mockReturnValue(
        new Promise<Response>((resolve) => {
          release = resolve;
        }),
      ),
    );
    render(<Leaderboard />);

    expect(await screen.findByText("Loading leaderboard")).toBeInTheDocument();
    release(jsonResponse(makeBoard(1, 1)));
    expect(await screen.findByText("pilot-1")).toBeInTheDocument();
    expect(screen.queryByText("Loading leaderboard")).not.toBeInTheDocument();
  });

  // frob:tests web/src/pages/Leaderboard.tsx::Leaderboard kind="unit"
  it("shows an empty state when nobody is ranked yet", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(makeBoard(0, 0))));
    render(<Leaderboard />);

    expect(await screen.findByText("No ranked players yet.")).toBeInTheDocument();
    expect(screen.queryByRole("listitem")).not.toBeInTheDocument();
  });

  // frob:tests web/src/pages/Leaderboard.tsx::Leaderboard kind="unit"
  it("offers Try again when the server is unavailable, then loads the board", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ detail: "leaderboard unavailable" }, 503))
      .mockResolvedValueOnce(jsonResponse(makeBoard(2, 2)));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<Leaderboard />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "leaderboard unavailable",
    );
    await user.click(screen.getByRole("button", { name: "Try again" }));

    expect(await screen.findByText("pilot-2")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  // frob:tests web/src/pages/Leaderboard.tsx::Leaderboard kind="unit"
  it("shows a generic message when the network fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));
    render(<Leaderboard />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/something went wrong/i);
  });

  // frob:tests web/src/pages/Leaderboard.tsx::Leaderboard kind="unit"
  it("lists each player once under StrictMode's double-run effects", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(() => Promise.resolve(jsonResponse(makeBoard(3, 3)))),
    );
    render(
      <StrictMode>
        <Leaderboard />
      </StrictMode>,
    );

    await screen.findByText("pilot-1");
    expect(screen.getAllByRole("listitem")).toHaveLength(3);
  });

  // frob:tests web/src/pages/Leaderboard.tsx::Leaderboard kind="unit"
  it("lays out for a 400px phone width without horizontal overflow", async () => {
    // jsdom cannot measure layout; assert the contract (see Profile.test.tsx).
    const longName = "x".repeat(60);
    const board = makeBoard(1, 1);
    board.entries[0] = { ...board.entries[0], username: longName };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(board)));
    const { container } = render(<Leaderboard />);

    await screen.findByText(longName);
    expect(overflowRisks(container, 400)).toEqual([]);
    expect(screen.getByText(longName)).toHaveClass("wrap-anywhere");
  });
});

describe("fetchLeaderboard", () => {
  // frob:tests web/src/api/leaderboard.ts::fetchLeaderboard kind="unit"
  it("requests the public endpoint and returns the parsed board", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(makeBoard(1, 1)));
    vi.stubGlobal("fetch", fetchMock);

    const board = await fetchLeaderboard();

    expect(board.total_players).toBe(1);
    expect(fetchMock.mock.calls[0][0]).toBe("/api/v1/leaderboard");
  });
});
