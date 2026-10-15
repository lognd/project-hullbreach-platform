// In-app navigation keeps the in-memory session (INV-006: a page load signs
// the user out by design), so links and post-login moves must never reload.
import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { RouterProvider } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { saveSession } from "@/auth/session";
import { AppLink } from "@/components/AppLink";
import { Header } from "@/components/Header";
import { navigate, usePathname } from "@/components/navigate";
import { TextField } from "@/components/TextField";

/** A JSON fetch Response with `status`. */
function jsonResponse(body: unknown, status: number) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

beforeEach(() => {
  window.history.pushState({}, "", "/");
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("navigate", () => {
  // frob:tests web/src/components/navigate.ts::navigate kind="unit"
  it("pushes the path and announces it with popstate", () => {
    const seen: string[] = [];
    const onPop = () => seen.push(window.location.pathname);
    window.addEventListener("popstate", onPop);
    navigate("/me/matches");
    window.removeEventListener("popstate", onPop);
    expect(window.location.pathname).toBe("/me/matches");
    expect(seen).toEqual(["/me/matches"]);
  });

  // frob:tests web/src/components/navigate.ts::usePathname kind="unit"
  it("usePathname re-renders on in-app navigation", () => {
    function Probe() {
      return <span>{usePathname()}</span>;
    }
    render(<Probe />);
    expect(screen.getByText("/")).toBeInTheDocument();
    act(() => navigate("/settings"));
    expect(screen.getByText("/settings")).toBeInTheDocument();
  });
});

describe("AppLink", () => {
  // frob:tests web/src/components/AppLink.tsx::AppLink kind="unit"
  it("handles a plain click in-app instead of letting the browser load the page", () => {
    render(<AppLink href="/me">Profile</AppLink>);
    const link = screen.getByRole("link", { name: "Profile" });
    expect(link).toHaveAttribute("href", "/me");
    const notPrevented = fireEvent.click(link);
    expect(notPrevented).toBe(false);
    expect(window.location.pathname).toBe("/me");
  });

  it("leaves modifier clicks (new tab) to the browser", () => {
    render(<AppLink href="/me">Profile</AppLink>);
    const notPrevented = fireEvent.click(screen.getByRole("link"), { ctrlKey: true });
    expect(notPrevented).toBe(true);
    expect(window.location.pathname).toBe("/");
  });
});

describe("Header navigation", () => {
  it("marks the current page's link with aria-current", () => {
    saveSession({ token: "tok-1", userId: "user-1", username: "flagship", role: "player" });
    window.history.pushState({}, "", "/settings");
    render(<Header />);
    expect(screen.getByRole("link", { name: "Settings" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Profile" })).not.toHaveAttribute("aria-current");
  });
});

describe("TextField", () => {
  // frob:tests web/src/components/TextField.tsx::TextField kind="unit"
  it("describes the input by its hint, or by its error alone once it has one", () => {
    const { rerender } = render(
      <TextField id="f" name="email" label="Email" hint="Blank keeps it." value="" error={undefined} onChange={() => {}} />,
    );
    const input = screen.getByLabelText("Email");
    expect(input).toHaveAccessibleDescription("Blank keeps it.");
    expect(input).not.toHaveAttribute("aria-invalid");
    rerender(
      <TextField id="f" name="email" label="Email" hint="Blank keeps it." value="" error="Email taken." onChange={() => {}} />,
    );
    expect(input).toHaveAccessibleDescription("Email taken.");
    expect(input).toHaveAttribute("aria-invalid", "true");
  });
});

describe("session across navigation", () => {
  // frob:tests web/src/pages/Login.tsx::Login kind="unit"
  it("stays signed in from login through a header link to the profile page", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith("/auth/login")) {
          return jsonResponse(
            {
              token: "tok-1",
              user: {
                id: "user-1",
                username: "flagship",
                email: "flagship@example.com",
                role: "player",
                currency: 450,
                rating: 1236,
                created_at: "2026-01-01T00:00:00Z",
              },
            },
            200,
          );
        }
        return jsonResponse(
          {
            id: "user-1",
            username: "flagship",
            email: "flagship@example.com",
            role: "player",
            currency: 450,
            rating: 1236,
            created_at: "2026-01-01T00:00:00Z",
            inventory: [],
            recent_matches: [],
          },
          200,
        );
      }),
    );
    window.history.pushState({}, "", "/login");
    vi.resetModules();
    const { router } = await import("@/router");
    // The router imports the fresh session module, so read that one.
    const session = await import("@/auth/session");
    render(<RouterProvider router={router} />);
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/username/i), "flagship");
    await user.type(screen.getByLabelText(/password/i), "correcthorse");
    await user.click(screen.getByRole("button", { name: /log ?in/i }));

    expect(await screen.findByRole("heading", { name: "Project Hullbreach" })).toBeInTheDocument();
    await user.click(within(screen.getByRole("banner")).getByRole("link", { name: "Profile" }));
    expect(await screen.findByText("1236")).toBeInTheDocument();
    expect(window.location.pathname).toBe("/me");
    expect(session.loadSession()?.username).toBe("flagship");
    session.clearSession();
  });

  it("never reloads the document from login through a header link and log out", async () => {
    // An in-app move is a history.pushState; a document load
    // (location.assign, a plain <a href> the browser follows) is not, and
    // jsdom silently ignores it. So every step must show up as a push.
    const pushes = vi.spyOn(window.history, "pushState");
    const pushed = () => pushes.mock.calls.map((call) => call[2]);
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith("/auth/login")) {
          return jsonResponse(
            {
              token: "tok-1",
              user: {
                id: "user-1",
                username: "flagship",
                email: "flagship@example.com",
                role: "player",
                currency: 450,
                rating: 1236,
                created_at: "2026-01-01T00:00:00Z",
              },
            },
            200,
          );
        }
        if (url.endsWith("/auth/logout")) {
          return new Response(null, { status: 204 });
        }
        return jsonResponse({ items: [], next_cursor: null }, 200);
      }),
    );
    window.history.pushState({}, "", "/login");
    pushes.mockClear();
    vi.resetModules();
    const { router } = await import("@/router");
    const session = await import("@/auth/session");
    render(<RouterProvider router={router} />);
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/username/i), "flagship");
    await user.type(screen.getByLabelText(/password/i), "correcthorse");
    await user.click(screen.getByRole("button", { name: /log ?in/i }));
    await waitFor(() => expect(pushed(), "login must navigate in-app, not reload").toEqual(["/"]));
    await screen.findByRole("heading", { name: "Project Hullbreach" });
    const banner = () => within(screen.getByRole("banner"));
    await user.click(banner().getByRole("link", { name: "Matches" }));
    await screen.findByRole("heading", { name: "Match history" });
    expect(session.loadSession()?.username).toBe("flagship");
    await user.click(banner().getByRole("button", { name: "Log out" }));
    await banner().findByRole("link", { name: "Log in" });

    expect(pushed()).toEqual(["/", "/me/matches", "/"]);
    expect(window.location.pathname).toBe("/");
    pushes.mockRestore();
  });
});
