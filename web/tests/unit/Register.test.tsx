// Failing-test skeleton for T-0017 (register page with inline validation
// errors, and the api/auth.ts client it shares with T-0021/T-0024). Every
// test targets web/src/pages/Register.tsx or web/src/api/auth.ts, neither of
// which exists yet; `it.fails` keeps the suite green until the real module
// lands and the import stops throwing, at which point the test goes red --
// the signal to move on to implementation.
//
// frob:ticket T-0017
import { render, screen, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

// frob:ticket T-0096
const registerModulePath = "../../src/pages/Register";
// frob:ticket T-0096
const authApiModulePath = "../../src/api/auth";

// frob:ticket T-0096
function jsonResponse(body: unknown, status: number) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("Register page", () => {
  it("shows field error next to the offending input", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse(
          { detail: "username already taken", field: "username" },
          409,
        ),
      ),
    );
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { Register } = await import(registerModulePath);
    const user = userEvent.setup();
    render(<Register />);
    await user.type(screen.getByLabelText(/username/i), "flagship");
    await user.type(screen.getByLabelText(/email/i), "flagship@example.com");
    await user.type(screen.getByLabelText(/password/i), "correcthorse");
    await user.click(screen.getByRole("button", { name: /register/i }));
    const usernameInput = screen.getByLabelText(/username/i);
    const describedBy = usernameInput.getAttribute("aria-describedby");
    expect(describedBy).toBeTruthy();
    const errorNode = document.getElementById(describedBy ?? "");
    expect(errorNode).toHaveTextContent(/username already taken/i);
  });

  it(
    "shows an email-taken error from a 409 response with field email",
    async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue(
          jsonResponse({ detail: "email already taken", field: "email" }, 409),
        ),
      );
      // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
      const { Register } = await import(registerModulePath);
      const user = userEvent.setup();
      render(<Register />);
      await user.type(screen.getByLabelText(/username/i), "flagship");
      await user.type(screen.getByLabelText(/email/i), "flagship@example.com");
      await user.type(screen.getByLabelText(/password/i), "correcthorse");
      await user.click(screen.getByRole("button", { name: /register/i }));
      const emailInput = screen.getByLabelText(/email/i);
      const describedBy = emailInput.getAttribute("aria-describedby");
      const errorNode = document.getElementById(describedBy ?? "");
      expect(errorNode).toHaveTextContent(/email already taken/i);
    },
  );

  it(
    "submits register with username, email, and password fields",
    async () => {
      const fetchMock = vi
        .fn()
        .mockResolvedValue(
          jsonResponse(
            {
              id: "user-1",
              username: "flagship",
              email: "flagship@example.com",
              role: "player",
              currency: 0,
              rating: 1200,
              created_at: "2026-01-01T00:00:00Z",
            },
            201,
          ),
        );
      vi.stubGlobal("fetch", fetchMock);
      // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
      const { Register } = await import(registerModulePath);
      const user = userEvent.setup();
      render(<Register />);
      await user.type(screen.getByLabelText(/username/i), "flagship");
      await user.type(screen.getByLabelText(/email/i), "flagship@example.com");
      await user.type(screen.getByLabelText(/password/i), "correcthorse");
      await user.click(screen.getByRole("button", { name: /register/i }));
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/auth/register"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            username: "flagship",
            email: "flagship@example.com",
            password: "correcthorse",
          }),
        }),
      );
    },
  );

  it(
    "shows a generic validation error when the API rejects the payload with 422",
    async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue(
          jsonResponse(
            { detail: [{ loc: ["body", "password"], msg: "too short" }] },
            422,
          ),
        ),
      );
      // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
      const { Register } = await import(registerModulePath);
      const user = userEvent.setup();
      render(<Register />);
      await user.type(screen.getByLabelText(/username/i), "flagship");
      await user.type(screen.getByLabelText(/email/i), "flagship@example.com");
      await user.type(screen.getByLabelText(/password/i), "short");
      await user.click(screen.getByRole("button", { name: /register/i }));
      expect(screen.getByRole("alert")).toBeInTheDocument();
    },
  );

  it(
    "navigates away from the register form after a successful registration",
    async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue(
          jsonResponse(
            {
              id: "user-1",
              username: "flagship",
              email: "flagship@example.com",
              role: "player",
              currency: 0,
              rating: 1200,
              created_at: "2026-01-01T00:00:00Z",
            },
            201,
          ),
        ),
      );
      // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
      const { Register } = await import(registerModulePath);
      const user = userEvent.setup();
      render(<Register />);
      await user.type(screen.getByLabelText(/username/i), "flagship");
      await user.type(screen.getByLabelText(/email/i), "flagship@example.com");
      await user.type(screen.getByLabelText(/password/i), "correcthorse");
      await user.click(screen.getByRole("button", { name: /register/i }));
      expect(
        screen.queryByRole("button", { name: /register/i }),
      ).not.toBeInTheDocument();
    },
  );
});

describe("api/auth.ts", () => {
  it(
    "register posts to /api/v1/auth/register with the request body",
    async () => {
      const fetchMock = vi
        .fn()
        .mockResolvedValue(
          jsonResponse(
            {
              id: "user-1",
              username: "flagship",
              email: "flagship@example.com",
              role: "player",
              currency: 0,
              rating: 1200,
              created_at: "2026-01-01T00:00:00Z",
            },
            201,
          ),
        );
      vi.stubGlobal("fetch", fetchMock);
      // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
      const { register } = await import(authApiModulePath);
      await register({
        username: "flagship",
        email: "flagship@example.com",
        password: "correcthorse",
      });
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/auth/register"),
        expect.objectContaining({ method: "POST" }),
      );
    },
  );

  it(
    "register throws an ApiError carrying the response detail and field on 409",
    async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue(
          jsonResponse(
            { detail: "username already taken", field: "username" },
            409,
          ),
        ),
      );
      // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
      const { register } = await import(authApiModulePath);
      await expect(
        register({
          username: "flagship",
          email: "flagship@example.com",
          password: "correcthorse",
        }),
      ).rejects.toMatchObject({
        status: 409,
        detail: "username already taken",
        field: "username",
      });
    },
  );

  it("login posts to /api/v1/auth/login with username and password", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse(
        {
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
        },
        200,
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { login } = await import(authApiModulePath);
    await login({ username: "flagship", password: "correcthorse" });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/auth/login"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it(
    "logout posts to /api/v1/auth/logout with a bearer Authorization header",
    async () => {
      const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
      vi.stubGlobal("fetch", fetchMock);
      // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
      const { logout } = await import(authApiModulePath);
      await logout("tok-1");
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/auth/logout"),
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({ Authorization: "Bearer tok-1" }),
        }),
      );
    },
  );

  it(
    "fetchSession sends a bearer Authorization header to GET /api/v1/auth/session",
    async () => {
      const fetchMock = vi
        .fn()
        .mockResolvedValue(
          jsonResponse({ user_id: "user-1", role: "player" }, 200),
        );
      vi.stubGlobal("fetch", fetchMock);
      // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
      const { fetchSession } = await import(authApiModulePath);
      await fetchSession("tok-1");
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/auth/session"),
        expect.objectContaining({
          headers: expect.objectContaining({ Authorization: "Bearer tok-1" }),
        }),
      );
    },
  );

  it("maps a 401 response to an ApiError with status 401", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          jsonResponse({ detail: "invalid username or password" }, 401),
        ),
    );
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { login } = await import(authApiModulePath);
    await expect(
      login({ username: "flagship", password: "wrong" }),
    ).rejects.toMatchObject({ status: 401 });
  });

  it("maps a 429 response to an ApiError with status 429", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          jsonResponse(
            { detail: "too many attempts, try again later" },
            429,
          ),
        ),
    );
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { login } = await import(authApiModulePath);
    await expect(
      login({ username: "flagship", password: "wrong" }),
    ).rejects.toMatchObject({ status: 429 });
  });
});
