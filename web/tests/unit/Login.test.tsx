// Failing-test skeleton for T-0021 (login page and persisted session across
// reloads). Every test targets web/src/pages/Login.tsx or
// web/src/auth/session.ts, neither of which exists yet; `it.fails` keeps the
// suite green until the real module lands and the import stops throwing, at
// which point the test goes red -- the signal to move on to implementation.
//
// frob:ticket T-0021
import { render, screen, cleanup, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// frob:ticket T-0096
const loginModulePath = "../../src/pages/Login";
// frob:ticket T-0096
const sessionModulePath = "../../src/auth/session";

// frob:ticket T-0096
function jsonResponse(body: unknown, status: number) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

// frob:ticket T-0096
const validLoginResponse = {
  token: "tok-1",
  user: {
    id: "user-1",
    username: "flagship",
    email: "flagship@example.com",
    role: "player",
    currency: 0,
    rating: 1200,
    created_at: "2026-01-01T00:00:00Z",
  },
};

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.localStorage.clear();
});

describe("Login page", () => {
  // frob:tests web/src/pages/Login.tsx::Login kind="unit"
  it("submits login with username and password fields", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse(validLoginResponse, 200));
    vi.stubGlobal("fetch", fetchMock);
    const { Login } = await import(loginModulePath);
    const user = userEvent.setup();
    render(<Login />);
    await user.type(screen.getByLabelText(/username/i), "flagship");
    await user.type(screen.getByLabelText(/password/i), "correcthorse");
    await user.click(screen.getByRole("button", { name: /log ?in/i }));
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/auth/login"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          username: "flagship",
          password: "correcthorse",
        }),
      }),
    );
  });

  // frob:tests web/src/api/auth.ts::login kind="unit"
  // frob:tests web/src/auth/session.ts::saveSession kind="unit"
  it(
    "keeps the session token out of localStorage and sessionStorage after login",
    async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue(jsonResponse(validLoginResponse, 200)),
      );
      const { Login } = await import(loginModulePath);
      const { loadSession } = await import(sessionModulePath);
      const user = userEvent.setup();
      render(<Login />);
      await user.type(screen.getByLabelText(/username/i), "flagship");
      await user.type(screen.getByLabelText(/password/i), "correcthorse");
      await user.click(screen.getByRole("button", { name: /log ?in/i }));
      await waitFor(() => expect(loadSession()?.token).toBe("tok-1"));
      for (const store of [window.localStorage, window.sessionStorage]) {
        expect(store.length).toBe(0);
        expect(JSON.stringify({ ...store })).not.toContain("tok-1");
      }
    },
  );

  it("keeps the user signed in across in-app navigation (same page load)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse(validLoginResponse, 200)),
    );
    const { Login } = await import(loginModulePath);
    const user = userEvent.setup();
    const { unmount } = render(<Login />);
    await user.type(screen.getByLabelText(/username/i), "flagship");
    await user.type(screen.getByLabelText(/password/i), "correcthorse");
    await user.click(screen.getByRole("button", { name: /log ?in/i }));
    unmount();

    const { useSession } = await import(sessionModulePath);
    function Probe() {
      const session = useSession();
      return <span>{session ? session.username : "signed-out"}</span>;
    }
    render(<Probe />);
    expect(screen.getByText("flagship")).toBeInTheDocument();
  });

  it(
    "shows a form-level error banner on 401 invalid credentials",
    async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue(
          jsonResponse({ detail: "invalid username or password" }, 401),
        ),
      );
      const { Login } = await import(loginModulePath);
      const user = userEvent.setup();
      render(<Login />);
      await user.type(screen.getByLabelText(/username/i), "flagship");
      await user.type(screen.getByLabelText(/password/i), "wrong");
      await user.click(screen.getByRole("button", { name: /log ?in/i }));
      expect(screen.getByRole("alert")).toHaveTextContent(
        /invalid username or password/i,
      );
    },
  );

  it(
    "shows a rate-limit message on 429 too many attempts",
    async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue(
          jsonResponse(
            { detail: "too many attempts, try again later" },
            429,
          ),
        ),
      );
      const { Login } = await import(loginModulePath);
      const user = userEvent.setup();
      render(<Login />);
      await user.type(screen.getByLabelText(/username/i), "flagship");
      await user.type(screen.getByLabelText(/password/i), "wrong");
      await user.click(screen.getByRole("button", { name: /log ?in/i }));
      expect(screen.getByRole("alert")).toHaveTextContent(
        /too many attempts/i,
      );
    },
  );

  it(
    "navigates to the landing page after a successful login",
    async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue(jsonResponse(validLoginResponse, 200)),
      );
      const { Login } = await import(loginModulePath);
      const user = userEvent.setup();
      render(<Login />);
      await user.type(screen.getByLabelText(/username/i), "flagship");
      await user.type(screen.getByLabelText(/password/i), "correcthorse");
      await user.click(screen.getByRole("button", { name: /log ?in/i }));
      expect(window.location.pathname).toBe("/");
    },
  );
});

describe("auth/session.ts", () => {
  // frob:tests web/src/auth/session.ts::loadSession kind="unit"
  it("loadSession is null on a fresh page load (nothing is persisted)", async () => {
    const { saveSession, loadSession } = await import(sessionModulePath);
    saveSession({ token: "tok-1", userId: "user-1", username: "flagship", role: "player" });
    vi.resetModules();
    const fresh = await import(sessionModulePath);
    expect(fresh.loadSession()).toBeNull();
    expect(loadSession()?.token).toBe("tok-1");
  });

  // frob:tests web/src/auth/session.ts::useSession kind="unit"
  it("ignores a token planted in localStorage", async () => {
    window.localStorage.setItem(
      "hullbreach.session",
      JSON.stringify({ token: "evil", userId: "u", username: "x", role: "player" }),
    );
    const { loadSession } = await import(sessionModulePath);
    expect(loadSession()).toBeNull();
  });

  // frob:tests web/src/auth/session.ts::clearSession kind="unit"
  it(
    "clears the stored session so loadSession returns null after clearSession",
    async () => {
      const { saveSession, clearSession, loadSession } = await import(
        sessionModulePath
      );
      saveSession({
        token: "tok-1",
        userId: "user-1",
        username: "flagship",
        role: "player",
      });
      clearSession();
      expect(loadSession()).toBeNull();
    },
  );

  it("useSession re-renders on saveSession and clearSession", async () => {
    const { useSession, saveSession, clearSession } = await import(
      sessionModulePath
    );
    function Probe() {
      const session = useSession();
      return <span>{session ? session.username : "signed-out"}</span>;
    }
    render(<Probe />);
    expect(screen.getByText("signed-out")).toBeInTheDocument();
    act(() =>
      saveSession({ token: "tok-1", userId: "user-1", username: "flagship", role: "player" }),
    );
    expect(await screen.findByText("flagship")).toBeInTheDocument();
    act(() => clearSession());
    expect(await screen.findByText("signed-out")).toBeInTheDocument();
  });
});
