// Failing-test skeleton for T-0021 (login page and persisted session across
// reloads). Every test targets web/src/pages/Login.tsx or
// web/src/auth/session.ts, neither of which exists yet; `it.fails` keeps the
// suite green until the real module lands and the import stops throwing, at
// which point the test goes red -- the signal to move on to implementation.
//
// frob:ticket 01M2H5T10N473QS7WDAWZH7HB5
import { render, screen, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// frob:ticket 01M2KR6R300KQMV7Y0QKK7HZ63
const loginModulePath = "../../src/pages/Login";
// frob:ticket 01M2KR6R300KQMV7Y0QKK7HZ63
const sessionModulePath = "../../src/auth/session";

// frob:ticket 01M2KR6R300KQMV7Y0QKK7HZ63
function jsonResponse(body: unknown, status: number) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

// frob:ticket 01M2KR6R300KQMV7Y0QKK7HZ63
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
    "persists the session to localStorage on successful login",
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
      const stored = window.localStorage.getItem("hullbreach.session");
      expect(stored).toBeTruthy();
      expect(JSON.parse(stored ?? "{}")).toMatchObject({
        token: "tok-1",
        username: "flagship",
      });
    },
  );

  it("keeps user signed in after reload", async () => {
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
  // frob:tests web/src/auth/session.ts::useSession kind="unit"
  it(
    "restores the session from localStorage synchronously on mount",
    async () => {
      window.localStorage.setItem(
        "hullbreach.session",
        JSON.stringify({
          token: "tok-1",
          userId: "user-1",
          username: "flagship",
          role: "player",
        }),
      );
      const { useSession } = await import(sessionModulePath);
      function Probe() {
        const session = useSession();
        return <span>{session ? session.username : "signed-out"}</span>;
      }
      render(<Probe />);
      expect(screen.getByText("flagship")).toBeInTheDocument();
    },
  );

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

  it(
    "useSession updates when a storage event fires from another tab",
    async () => {
      const { useSession } = await import(sessionModulePath);
      function Probe() {
        const session = useSession();
        return <span>{session ? session.username : "signed-out"}</span>;
      }
      render(<Probe />);
      expect(screen.getByText("signed-out")).toBeInTheDocument();

      window.localStorage.setItem(
        "hullbreach.session",
        JSON.stringify({
          token: "tok-1",
          userId: "user-1",
          username: "flagship",
          role: "player",
        }),
      );
      window.dispatchEvent(new StorageEvent("storage", { key: "hullbreach.session" }));
      expect(await screen.findByText("flagship")).toBeInTheDocument();
    },
  );

  it(
    "loadSession returns null for malformed JSON in localStorage",
    async () => {
      window.localStorage.setItem("hullbreach.session", "{not-json");
      const { loadSession } = await import(sessionModulePath);
      expect(loadSession()).toBeNull();
    },
  );
});
