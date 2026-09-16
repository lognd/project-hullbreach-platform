// Failing-test skeleton for T-0044 (router, page shell, Header/Footer) and
// T-0024 (logout control in the header). Every test below targets a module
// that does not exist yet (web/src/router.tsx, web/src/components/Header.tsx,
// web/src/components/Footer.tsx, web/src/auth/session.ts, web/src/App.tsx's
// shell form); `it.fails` keeps the suite green while that is true and turns
// red -- the intended signal to move on to implementation -- the moment the
// real module lands and the import stops throwing.
//
// frob:ticket T-0044
// frob:ticket T-0024
import { render, screen, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Dynamic import specifiers are read from a variable (not a string literal)
// so `tsc --noEmit` treats the import() as untyped rather than trying to
// resolve a module that does not exist yet on this branch.
// frob:ticket T-0096
const headerModulePath = "../../src/components/Header";
// frob:ticket T-0096
const footerModulePath = "../../src/components/Footer";
// frob:ticket T-0096
const routerModulePath = "../../src/router";
// frob:ticket T-0096
const appModulePath = "../../src/App";
// frob:ticket T-0096
const sessionModulePath = "../../src/auth/session";
// frob:ticket T-0096
const routerDomModulePath = "react-router-dom";

// frob:ticket T-0096
function stubFetchOnce(body: unknown, init: ResponseInit = { status: 204 }) {
  const response = new Response(
    body === undefined ? null : JSON.stringify(body),
    init,
  );
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(response satisfies Response),
  );
}

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.localStorage.clear();
});

describe("Header (signed out)", () => {
  it("renders the brand", async () => {
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { Header } = await import(headerModulePath);
    render(<Header />);
    expect(screen.getByText(/hullbreach/i)).toBeInTheDocument();
  });

  it("shows Register and Login links when signed out", async () => {
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { Header } = await import(headerModulePath);
    render(<Header />);
    expect(screen.getByRole("link", { name: /register/i })).toHaveAttribute(
      "href",
      "/register",
    );
    expect(screen.getByRole("link", { name: /log ?in/i })).toHaveAttribute(
      "href",
      "/login",
    );
  });

  it(
    "renders every interactive control as a real anchor or button element",
    async () => {
      // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
      const { Header } = await import(headerModulePath);
      render(<Header />);
      const controls = [
        ...screen.getAllByRole("link"),
        ...screen.getAllByRole("button"),
      ];
      expect(controls.length).toBeGreaterThan(0);
      for (const control of controls) {
        expect(["A", "BUTTON"]).toContain(control.tagName);
      }
    },
  );
});

describe("Header (signed in)", () => {
  it("shows username and a Log out control when signed in", async () => {
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const session = await import(sessionModulePath);
    session.saveSession({
      token: "tok-1",
      userId: "user-1",
      username: "flagship",
      role: "player",
    });
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { Header } = await import(headerModulePath);
    render(<Header />);
    expect(screen.getByText("flagship")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /log ?out/i }),
    ).toBeInTheDocument();
  });

  it.fails("clears session and navigates home on logout click", async () => {
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const session = await import(sessionModulePath);
    session.saveSession({
      token: "tok-1",
      userId: "user-1",
      username: "flagship",
      role: "player",
    });
    stubFetchOnce(undefined, { status: 204 });
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { Header } = await import(headerModulePath);
    const user = userEvent.setup();
    render(<Header />);
    await user.click(screen.getByRole("button", { name: /log ?out/i }));
    expect(session.loadSession()).toBeNull();
    expect(window.location.pathname).toBe("/");
  });

  it.fails(
    "logout button calls POST /api/v1/auth/logout with the bearer token",
    async () => {
      // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
      const session = await import(sessionModulePath);
      session.saveSession({
        token: "tok-1",
        userId: "user-1",
        username: "flagship",
        role: "player",
      });
      stubFetchOnce(undefined, { status: 204 });
      // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
      const { Header } = await import(headerModulePath);
      const user = userEvent.setup();
      render(<Header />);
      await user.click(screen.getByRole("button", { name: /log ?out/i }));
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/auth/logout"),
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            Authorization: "Bearer tok-1",
          }),
        }),
      );
    },
  );
});

describe("Header keyboard access", () => {
  it(
    "tab order matches visual order and Enter activates each control",
    async () => {
      // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
      const { Header } = await import(headerModulePath);
      const activated: string[] = [];
      render(<Header />);
      const controls = [
        ...screen.getAllByRole("link"),
        ...screen.getAllByRole("button"),
      ];
      const user = userEvent.setup();
      for (const control of controls) {
        control.addEventListener("click", () =>
          activated.push(control.textContent ?? ""),
        );
      }
      await user.tab();
      for (let i = 0; i < controls.length; i += 1) {
        expect(document.activeElement).toBe(controls[i]);
        await user.keyboard("{Enter}");
        await user.tab();
      }
      expect(activated.length).toBe(controls.length);
    },
  );
});

describe("Footer", () => {
  it("renders the footer with cookie and data policy links", async () => {
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { Footer } = await import(footerModulePath);
    render(<Footer />);
    expect(
      screen.getByRole("link", { name: /cookie/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /data policy/i }),
    ).toBeInTheDocument();
  });
});

describe("router", () => {
  // Each test below pushes a different path and then dynamically re-imports
  // router.tsx; without resetting the module registry first, the second and
  // later imports would return the already-cached router (and its state,
  // fixed at the first import's location) instead of a fresh one that reads
  // the just-pushed path.
  beforeEach(() => {
    vi.resetModules();
  });

  it("renders the landing page at /", async () => {
    window.history.pushState({}, "", "/");
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { router } = await import(routerModulePath);
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { RouterProvider } = await import(routerDomModulePath);
    render(<RouterProvider router={router} />);
    expect(
      screen.getByRole("heading", { name: "Project Hullbreach" }),
    ).toBeInTheDocument();
  });

  it("renders the register page at /register", async () => {
    window.history.pushState({}, "", "/register");
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { router } = await import(routerModulePath);
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { RouterProvider } = await import(routerDomModulePath);
    render(<RouterProvider router={router} />);
    expect(
      screen.getByRole("heading", { name: /register/i }),
    ).toBeInTheDocument();
  });

  it("renders the login page at /login", async () => {
    window.history.pushState({}, "", "/login");
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { router } = await import(routerModulePath);
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { RouterProvider } = await import(routerDomModulePath);
    render(<RouterProvider router={router} />);
    expect(
      screen.getByRole("heading", { name: /log ?in/i }),
    ).toBeInTheDocument();
  });

  it("renders a not-found page for an unknown path", async () => {
    window.history.pushState({}, "", "/does-not-exist");
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { router } = await import(routerModulePath);
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { RouterProvider } = await import(routerDomModulePath);
    render(<RouterProvider router={router} />);
    expect(screen.getByText(/not found/i)).toBeInTheDocument();
  });
});

describe("App shell", () => {
  it("renders Header and Footer around the routed page", async () => {
    // frob:waive OPAQUE001 reason="specifier is a variable so vite/vitest treat the import as runtime-resolved instead of eagerly failing to resolve a not-yet-existing module at transform time (a literal specifier here breaks vite:import-analysis even with @vite-ignore); the module path is a single file-scoped const, not user input" permanent="true"
    const { App } = await import(appModulePath);
    render(<App />);
    expect(
      screen.getByRole("banner"),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("contentinfo"),
    ).toBeInTheDocument();
  });
});
