import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { COOKIE_NOTICE_KEY } from "@/components/CookieNotice";
import { CookiePolicy } from "@/pages/CookiePolicy";

afterEach(cleanup);

describe("CookiePolicy", () => {
  // frob:tests web/src/pages/CookiePolicy.tsx::CookiePolicy kind="unit"
  it("names the session cookie and the one localStorage key", () => {
    render(<CookiePolicy />);
    expect(screen.getByText(/sets one cookie/i)).toBeInTheDocument();
    expect(screen.getByText("hullbreach_session")).toBeInTheDocument();
    expect(screen.getByText(/HttpOnly/)).toBeInTheDocument();
    expect(screen.queryByText(/does not set cookies/i)).toBeNull();
    expect(screen.queryByText(/signs you out\./i)).toBeNull();
    expect(screen.getByText(COOKIE_NOTICE_KEY)).toBeInTheDocument();
  });

  // frob:tests web/src/pages/CookiePolicy.tsx::CookiePolicy kind="unit"
  it("links on to the data policy", () => {
    render(<CookiePolicy />);
    expect(screen.getByRole("link", { name: "data policy" })).toHaveAttribute(
      "href",
      "/data-policy",
    );
  });
});
