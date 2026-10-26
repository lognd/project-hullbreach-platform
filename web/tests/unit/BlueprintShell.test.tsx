// Blueprint-direction pieces: breadcrumb and page title block, the ELO trace
// chart (inset, clipped, placeholder), the header's active state, and a
// no-horizontal-overflow check on the pages' class lists at a phone width.
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { EloTrace, traceGeometry } from "@/components/EloTrace";
import { Header } from "@/components/Header";
import { Breadcrumb, Page } from "@/components/Page";
import { saveSession } from "@/auth/session";
import { overflowRisks } from "../support/layout";

beforeEach(() => {
  window.localStorage.clear();
  window.history.pushState({}, "", "/");
});

describe("Page and Breadcrumb", () => {
  // frob:tests web/src/components/Page.tsx::Breadcrumb kind="unit"
  it("shows Home plus the crumbs and marks only the last as the current page", () => {
    render(<Breadcrumb crumbs={[{ label: "Profile", href: "/me" }, { label: "Matches" }]} />);
    const nav = screen.getByRole("navigation", { name: "Breadcrumb" });
    expect(nav).toHaveTextContent("Home/Profile/Matches");
    expect(screen.getByRole("link", { name: "Home" })).toHaveAttribute("href", "/");
    expect(screen.getByRole("link", { name: "Profile" })).toHaveAttribute("href", "/me");
    expect(screen.getByText("Matches")).toHaveAttribute("aria-current", "page");
    expect(screen.queryAllByRole("listitem")).toHaveLength(0);
  });

  // frob:tests web/src/components/Page.tsx::Page kind="unit"
  it("gives a Page a display-face h1 and a one-line purpose", () => {
    render(<Page crumbs={[{ label: "Settings" }]} title="Account settings" purpose="Change things." />);
    expect(screen.getByRole("heading", { level: 1, name: "Account settings" })).toHaveClass("font-display", "uppercase");
    expect(screen.getByText("Change things.")).toBeInTheDocument();
  });
});

describe("EloTrace", () => {
  // frob:tests web/src/components/EloTrace.tsx::traceGeometry kind="unit"
  it("keeps every plotted point inside the viewBox, flat series included", () => {
    for (const ratings of [[1200, 1212, 1195, 1230], [1200, 1200], [1500]]) {
      for (const point of traceGeometry(ratings)) {
        expect(point.x).toBeGreaterThanOrEqual(7);
        expect(point.x).toBeLessThanOrEqual(353);
        expect(point.y).toBeGreaterThanOrEqual(7);
        expect(point.y).toBeLessThanOrEqual(133);
      }
    }
  });

  // frob:tests web/src/components/EloTrace.tsx::EloTrace kind="unit"
  it("draws a clipped polyline with non-scaling strokes and an orange newest marker", () => {
    const { container } = render(<EloTrace ratings={[1200, 1212, 1195, 1236]} />);
    expect(screen.getByRole("img", { name: /from 1200 to 1236/ })).toHaveClass("overflow-hidden");
    expect(container.querySelector("polyline")).toHaveAttribute("vector-effect", "non-scaling-stroke");
    expect(container.querySelectorAll("rect")).toHaveLength(4);
    expect(container.querySelectorAll('rect[fill="var(--color-signal)"]')).toHaveLength(1);
    expect(container.firstElementChild).toHaveTextContent("Last 3 matches: 1200 to 1236");
  });

  // frob:tests web/src/components/EloTrace.tsx::EloTrace kind="unit"
  it("shows a hatched placeholder with an opaque label chip when there is too little data", () => {
    const { container } = render(<EloTrace ratings={[1200]} />);
    expect(container.querySelector("pattern")).not.toBeNull();
    expect(container.querySelector("polyline")).toBeNull();
    expect(screen.getByText(/no data yet/i)).toHaveClass("bg-panel", "border");
    expect(container.querySelector("pattern path")).toHaveAttribute("vector-effect", "non-scaling-stroke");
  });

  // frob:tests web/src/components/EloTrace.tsx::EloTrace kind="unit"
  it("has no fixed width that could overflow a 390px viewport", () => {
    const { container } = render(<EloTrace ratings={[1200, 1210]} />);
    expect(overflowRisks(container, 390)).toEqual([]);
  });
});

describe("Header active state", () => {
  // frob:tests web/src/components/Header.tsx::Header kind="unit"
  it("marks the current section with aria-current and offers a clear Log out", () => {
    saveSession({ token: "t", userId: "u", username: "demo_pilot", role: "player" });
    window.history.pushState({}, "", "/me/matches");
    render(<Header />);
    expect(screen.getByRole("link", { name: "Matches" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Profile" })).not.toHaveAttribute("aria-current");
    expect(screen.getByRole("button", { name: "Log out" })).toBeInTheDocument();
  });
});
