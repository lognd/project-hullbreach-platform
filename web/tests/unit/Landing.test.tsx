import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { saveSession } from "@/auth/session";
import { Landing } from "@/pages/Landing";

afterEach(cleanup);

describe("Landing", () => {
  // frob:tests web/src/pages/Landing.tsx::Landing kind="unit"
  it("states the premise under the wordmark and tagline", () => {
    render(<Landing />);
    expect(
      screen.getByRole("heading", { level: 1, name: "Project Hullbreach" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Build. Breach. Claim the void." }),
    ).toBeInTheDocument();
    expect(screen.getByText(/spaceship one block at a time/i)).toBeInTheDocument();
  });

  // frob:tests web/src/pages/Landing.tsx::Landing kind="unit"
  it("offers register and login when signed out", () => {
    render(<Landing />);
    expect(screen.getByRole("link", { name: "Create account" })).toHaveAttribute(
      "href",
      "/register",
    );
    expect(screen.getByRole("link", { name: "Log in" })).toHaveAttribute(
      "href",
      "/login",
    );
  });

  // frob:tests web/src/pages/Landing.tsx::Landing kind="unit"
  it("offers profile links instead once signed in", () => {
    saveSession({ token: "t", userId: "u", username: "ace", role: "player" });
    render(<Landing />);
    expect(screen.getByRole("link", { name: "Profile" })).toHaveAttribute(
      "href",
      "/me",
    );
    expect(screen.queryByRole("link", { name: "Create account" })).toBeNull();
  });

  // frob:tests web/src/pages/Landing.tsx::Landing kind="unit"
  it("says plainly that no download is published rather than linking a dead file", () => {
    render(<Landing />);
    expect(screen.getByText(/not published yet/i)).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /download/i })).toBeNull();
  });

  // frob:tests web/src/pages/Landing.tsx::Landing kind="unit"
  it("lists the four beats of a match in order and shows the ship drawing", () => {
    render(<Landing />);
    const items = within(screen.getByRole("list")).getAllByRole("listitem");
    expect(items.map((item) => item.textContent)).toEqual([
      expect.stringMatching(/^01 Build/),
      expect.stringMatching(/^02 Fly/),
      expect.stringMatching(/^03 Breach/),
      expect.stringMatching(/^04 Rank/),
    ]);
    expect(screen.getByRole("img", { name: /spaceship/i })).toBeInTheDocument();
  });
});
