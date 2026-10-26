import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { COOKIE_NOTICE_KEY } from "@/components/CookieNotice";
import { CookiePolicy } from "@/pages/CookiePolicy";

afterEach(cleanup);

describe("CookiePolicy", () => {
  // frob:tests web/src/pages/CookiePolicy.tsx::CookiePolicy kind="unit"
  it("says no cookies are set and names the one localStorage key", () => {
    render(<CookiePolicy />);
    expect(screen.getByText(/does not set cookies/i)).toBeInTheDocument();
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
