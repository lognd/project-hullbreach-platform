import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { CookieNotice, COOKIE_NOTICE_KEY } from "@/components/CookieNotice";

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  window.localStorage.clear();
});

describe("CookieNotice", () => {
  // frob:tests web/src/components/CookieNotice.tsx::CookieNotice kind="unit"
  it("shows on a first visit with a link to the cookie policy", () => {
    render(<CookieNotice />);
    expect(screen.getByRole("region", { name: "Cookie notice" })).toBeInTheDocument();
    expect(screen.getByText(/one strictly necessary session cookie/i)).toBeInTheDocument();
    expect(screen.queryByText(/sets no cookies/i)).toBeNull();
    expect(screen.getByRole("link", { name: "Cookie policy" })).toHaveAttribute(
      "href",
      "/cookie-policy",
    );
  });

  // frob:tests web/src/components/CookieNotice.tsx::CookieNotice kind="unit"
  it("hides and stores the flag when dismissed", async () => {
    const user = userEvent.setup();
    render(<CookieNotice />);
    await user.click(screen.getByRole("button", { name: "Dismiss" }));
    expect(screen.queryByRole("region", { name: "Cookie notice" })).toBeNull();
    expect(window.localStorage.getItem(COOKIE_NOTICE_KEY)).toBe("dismissed");
  });

  // frob:tests web/src/components/CookieNotice.tsx::CookieNotice kind="unit"
  it("does not show after a dismissed notice and a reload", async () => {
    const user = userEvent.setup();
    const first = render(<CookieNotice />);
    await user.click(screen.getByRole("button", { name: "Dismiss" }));
    first.unmount();
    render(<CookieNotice />);
    expect(screen.queryByRole("region", { name: "Cookie notice" })).toBeNull();
  });

  // frob:tests web/src/components/CookieNotice.tsx::CookieNotice kind="unit"
  it("still dismisses for this page load when storage throws", async () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    const user = userEvent.setup();
    render(<CookieNotice />);
    await user.click(screen.getByRole("button", { name: "Dismiss" }));
    expect(screen.queryByRole("region", { name: "Cookie notice" })).toBeNull();
  });
});
