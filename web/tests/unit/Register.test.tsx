// Failing-test skeleton for T-0017 (register page with inline validation
// errors, and the api/auth.ts client it shares with T-0021/T-0024). Every
// test targets web/src/pages/Register.tsx or web/src/api/auth.ts, neither of
// which exists yet; `it.fails` keeps the suite green until the real module
// lands and the import stops throwing, at which point the test goes red --
// the signal to move on to implementation.
//
// frob:ticket 01M2H5T10HEMPGEZ7JBHEZV0RC
import { render, screen, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

// frob:ticket 01M2KR6R300KQMV7Y0QKK7HZ63
const registerModulePath = "../../src/pages/Register";
// frob:ticket 01M2KR6R300KQMV7Y0QKK7HZ63
const authApiModulePath = "../../src/api/auth";

// frob:ticket 01M2KR6R300KQMV7Y0QKK7HZ63
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
  // frob:tests web/src/pages/Register.tsx::Register kind="unit"
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
  // frob:tests web/src/api/auth.ts::register kind="unit"
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

  // frob:tests web/src/api/auth.ts::ApiError kind="unit"
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

  // frob:tests web/src/api/auth.ts::login kind="unit"
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
    const { login } = await import(authApiModulePath);
    await login({ username: "flagship", password: "correcthorse" });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/auth/login"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  // frob:tests web/src/api/auth.ts::logout kind="unit"
  it(
    "logout posts to /api/v1/auth/logout with a bearer Authorization header",
    async () => {
      const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
      vi.stubGlobal("fetch", fetchMock);
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

  it("maps a 401 response to an ApiError with status 401", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          jsonResponse({ detail: "invalid username or password" }, 401),
        ),
    );
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
    const { login } = await import(authApiModulePath);
    await expect(
      login({ username: "flagship", password: "wrong" }),
    ).rejects.toMatchObject({ status: 429 });
  });
});

// frob:ticket 01M5XX28K491XN5RNGABW0Q5RP
const REGISTER_422 = {
  detail: "password must be at least 8 characters",
  field: "password",
  errors: [
    { field: "email", detail: "enter a valid email address" },
    { field: "password", detail: "password must be at least 8 characters" },
  ],
};

describe("Register page per-field errors", () => {
  // frob:tests web/src/pages/Register.tsx::Register kind="unit"
  it("shows every rejected field's reason inline next to its input", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse(REGISTER_422, 422)),
    );
    const { Register } = await import(registerModulePath);
    const user = userEvent.setup();
    render(<Register />);
    await user.type(screen.getByLabelText(/username/i), "flagship");
    await user.type(screen.getByLabelText(/email/i), "nope");
    await user.type(screen.getByLabelText(/password/i), "1234");
    await user.click(screen.getByRole("button", { name: /register/i }));

    const passwordNode = document.getElementById(
      screen.getByLabelText(/password/i).getAttribute("aria-describedby") ?? "",
    );
    expect(passwordNode).toHaveTextContent(
      "password must be at least 8 characters",
    );
    const emailNode = document.getElementById(
      screen.getByLabelText(/email/i).getAttribute("aria-describedby") ?? "",
    );
    expect(emailNode).toHaveTextContent("enter a valid email address");
  });

  // frob:tests web/src/pages/Register.tsx::Register kind="unit"
  it("submits even when the browser would call the email invalid", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse(REGISTER_422, 422));
    vi.stubGlobal("fetch", fetchMock);
    const { Register } = await import(registerModulePath);
    const user = userEvent.setup();
    render(<Register />);
    await user.type(screen.getByLabelText(/email/i), "nope");
    await user.click(screen.getByRole("button", { name: /register/i }));
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});

describe("api/auth.ts field errors", () => {
  // frob:tests web/src/api/auth.ts::errorFromResponse kind="unit"
  it("exposes register's errors list as ApiError.fieldErrors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse(REGISTER_422, 422)),
    );
    const { register } = await import(authApiModulePath);
    await expect(
      register({ username: "flagship", email: "nope", password: "1234" }),
    ).rejects.toMatchObject({
      status: 422,
      field: "password",
      fieldErrors: {
        email: "enter a valid email address",
        password: "password must be at least 8 characters",
      },
    });
  });
});
