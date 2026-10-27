import { cleanup, render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fetchMatch } from "@/api/me";
import { saveSession } from "@/auth/session";
import { MatchDetail } from "@/pages/MatchDetail";
import { makeMatchDetail } from "../fixtures/me";

/** A JSON Response, as the server would send it. */
function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

/** Renders the page at /me/matches/:id the way the router mounts it. */
function renderAt(id: string): void {
  render(
    <MemoryRouter initialEntries={[`/me/matches/${id}`]}>
      <Routes>
        <Route path="me/matches/:matchId" element={<MatchDetail />} />
      </Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  window.localStorage.clear();
  saveSession({ token: "tok-1", userId: "user-1", username: "flagship", role: "player" });
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.localStorage.clear();
});

describe("MatchDetail page", () => {
  // frob:tests web/src/pages/MatchDetail.tsx::MatchDetail kind="unit"
  it("shows the result, duration, ELO move and both players' lines", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(makeMatchDetail(0)));
    vi.stubGlobal("fetch", fetchMock);
    renderAt("match-0");

    expect(await screen.findByRole("heading", { name: /victory/i })).toBeInTheDocument();
    expect(screen.getByText("5:00")).toBeInTheDocument();
    expect(screen.getByTestId("your-delta")).toHaveTextContent("+12");
    const rows = screen.getAllByRole("listitem");
    expect(rows).toHaveLength(2);
    expect(within(rows[0]).getByText("flagship")).toBeInTheDocument();
    expect(rows[0]).toHaveTextContent("You");
    expect(rows[0]).toHaveTextContent("damage dealt 900");
    expect(rows[1]).toHaveTextContent("rival-0");
    expect(rows[1]).toHaveTextContent("-12");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/me/matches/match-0",
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer tok-1" }),
      }),
    );
  });

  // frob:tests web/src/pages/MatchDetail.tsx::MatchDetail kind="unit"
  it("says defeat for a loss", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(makeMatchDetail(1))));
    renderAt("match-1");

    expect(await screen.findByRole("heading", { name: /defeat/i })).toBeInTheDocument();
    expect(screen.getByTestId("your-delta")).toHaveTextContent("-12");
  });

  // frob:tests web/src/pages/MatchDetail.tsx::MatchDetail kind="unit"
  it("shows a not-found notice with a way back on 404", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ detail: "match not found" }, 404)),
    );
    renderAt("nope");

    expect(await screen.findByRole("alert")).toHaveTextContent("match not found");
    expect(screen.getByRole("link", { name: /back to matches/i })).toHaveAttribute(
      "href",
      "/me/matches",
    );
  });

  // frob:tests web/src/api/me.ts::fetchMatch kind="unit"
  it("fetchMatch GETs the match with the bearer token and encodes the id", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(makeMatchDetail(0)));
    vi.stubGlobal("fetch", fetchMock);

    const detail = await fetchMatch("tok-1", "a/b");

    expect(detail.players).toHaveLength(2);
    expect(fetchMock.mock.calls[0][0]).toBe("/api/v1/me/matches/a%2Fb");
  });
});
