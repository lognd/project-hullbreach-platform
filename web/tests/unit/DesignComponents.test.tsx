// Shared presentational components: one button look for links and buttons,
// and the landing hull readout exposed to assistive tech as a single image.
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { Button, ButtonLink } from "@/components/Button";
import { HullReadout } from "@/components/HullReadout";

beforeEach(() => {
  window.history.pushState({}, "", "/");
});

describe("ButtonLink", () => {
  // frob:tests web/src/components/Button.tsx::ButtonLink kind="unit"
  it("looks like the same-variant Button and navigates in-app", () => {
    render(
      <>
        <Button variant="primary">Save</Button>
        <ButtonLink href="/register" variant="primary">
          Register
        </ButtonLink>
      </>,
    );
    const link = screen.getByRole("link", { name: "Register" });
    expect(link.className).toBe(screen.getByRole("button", { name: "Save" }).className);
    expect(fireEvent.click(link)).toBe(false);
    expect(window.location.pathname).toBe("/register");
  });
});

describe("HullReadout", () => {
  // frob:tests web/src/components/HullReadout.tsx::HullReadout kind="unit"
  it("is one labelled image with a legend for every stress color", () => {
    render(<HullReadout />);
    expect(screen.getByRole("img", { name: /hull stress/i })).toBeInTheDocument();
    for (const word of ["Holding", "Stressed", "Breaching"]) {
      expect(screen.getByText(word)).toBeInTheDocument();
    }
  });
});
