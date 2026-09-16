import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "@/App";

// App's job changed from rendering the landing page itself to being the page
// shell (Header/Outlet/Footer, see docs/design/sprint-1.md sec.6) once
// T-0044 added routing; the landing heading now lives in router.tsx's
// Landing route (covered by web/tests/unit/Header.test.tsx's "router"
// describe block), so this smoke test asserts the shell responsibility that
// replaced it instead.
describe("App", () => {
  it("renders the header and footer landmarks around the routed content", () => {
    render(<App />);
    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
  });
});
