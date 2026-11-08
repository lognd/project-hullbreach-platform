import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { clearSession, saveSession } from "@/auth/session";
import { AdminPlayers } from "@/pages/admin/Players";

/** A JSON Response, as the server would send it. */
function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

const ROW = { id: "p1", username: "pilot", role: "player", rating: 1500, suspended: false };
const DETAIL = {
  ...ROW,
  email: "p@example.com",
  balance: 10,
  created_at: "2026-01-01T00:00:00Z",
  suspended_reason: null,
  moderation: [],
  trust_events: [],
};

beforeEach(() => {
  clearSession();
  window.history.pushState({}, "", "/admin/players");
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  clearSession();
});

describe("AdminPlayers page", () => {
  // frob:tests web/src/pages/admin/Players.tsx::AdminPlayers kind="unit"
  it("redirects a player session away from /admin without calling the API", () => {
    saveSession({ token: "t", userId: "u", username: "pilot", role: "player" });
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    render(<AdminPlayers />);
    expect(window.location.pathname).toBe("/");
    expect(screen.queryByText("Players")).not.toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  // frob:tests web/src/pages/admin/Players.tsx::AdminPlayers kind="unit"
  it("lets an admin search and suspend a player with a reason", async () => {
    saveSession({ token: "adm", userId: "a", username: "root", role: "admin" });
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse([ROW]))
      .mockResolvedValueOnce(jsonResponse(DETAIL))
      .mockResolvedValueOnce(
        jsonResponse({ ...DETAIL, suspended: true, suspended_reason: "cheating" }),
      );
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<AdminPlayers />);

    await user.type(screen.getByLabelText("Username"), "pil");
    await user.click(screen.getByRole("button", { name: "Search" }));
    await user.click(await screen.findByRole("button", { name: "Open pilot" }));
    await user.type(await screen.findByLabelText("Reason"), "cheating");
    await user.click(screen.getByRole("button", { name: "Suspend" }));

    expect(await screen.findByText("Suspended: cheating")).toBeInTheDocument();
    const init = fetchMock.mock.calls[2]?.[1] as RequestInit;
    expect(fetchMock.mock.calls[2]?.[0]).toBe("/api/v1/admin/players/p1/suspend");
    expect(JSON.parse(init.body as string)).toEqual({ reason: "cheating" });
    expect(init.headers).toHaveProperty("Authorization", "Bearer adm");
  });
});
