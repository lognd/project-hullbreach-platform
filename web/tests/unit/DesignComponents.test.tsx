// Shared presentational components: one button look for links and buttons,
// and the landing hull readout exposed to assistive tech as a single image.
import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { Button, ButtonLink } from "@/components/Button";
import { HullReadout } from "@/components/HullReadout";
import { MatchColumns } from "@/components/MatchItem";
import { EmptyState, Panel, SkeletonRows, StatTile } from "@/components/Readout";
import { TextField } from "@/components/TextField";

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

describe("Readout components", () => {
  // frob:tests web/src/components/Readout.tsx::StatTile kind="unit"
  it("renders a StatTile as a mono tabular term and value", () => {
    const { container } = render(
      <dl>
        <StatTile label="ELO" value={1236} tone="accent" />
      </dl>,
    );
    expect(container.querySelector("dt")).toHaveTextContent("ELO");
    const dd = container.querySelector("dd");
    expect(dd).toHaveTextContent("1236");
    expect(dd).toHaveClass("font-mono", "tabular-nums", "text-accent");
  });

  // frob:tests web/src/components/Readout.tsx::EmptyState kind="unit"
  it("shows the title, hint and action of an EmptyState", () => {
    render(<EmptyState title="Nothing here." hint="Add one." action={<button>Go</button>} />);
    expect(screen.getByText("Nothing here.")).toBeInTheDocument();
    expect(screen.getByText("Add one.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Go" })).toBeInTheDocument();
  });

  // frob:tests web/src/components/Readout.tsx::SkeletonRows kind="unit"
  it("hides SkeletonRows from assistive tech", () => {
    const { container } = render(<SkeletonRows count={4} />);
    const root = container.firstElementChild;
    expect(root).toHaveAttribute("aria-hidden", "true");
    expect(root?.children).toHaveLength(4);
  });

  // frob:tests web/src/components/Readout.tsx::Panel kind="unit"
  it("draws two decorative corner brackets on a Panel", () => {
    const { container } = render(<Panel>Body</Panel>);
    expect(screen.getByText("Body")).toBeInTheDocument();
    expect(container.querySelectorAll("span[aria-hidden]")).toHaveLength(2);
  });
});

describe("TextField password toggle", () => {
  // frob:tests web/src/components/TextField.tsx::TextField kind="unit"
  it("switches a password field between hidden and visible", async () => {
    render(<TextField id="pw" name="pw" label="Password" type="password" value="" error={undefined} onChange={() => {}} />);
    const input = screen.getByLabelText(/password/i);
    expect(input).toHaveAttribute("type", "password");
    await userEvent.click(screen.getByRole("button", { name: "Show" }));
    expect(input).toHaveAttribute("type", "text");
    expect(screen.getByRole("button", { name: "Hide" })).toHaveAttribute("aria-pressed", "true");
    await userEvent.click(screen.getByRole("button", { name: "Hide" }));
    expect(input).toHaveAttribute("type", "password");
  });

  // frob:tests web/src/components/TextField.tsx::TextField kind="unit"
  it("adds no toggle to a text field", () => {
    render(<TextField id="n" name="n" label="Name" type="text" value="" error={undefined} onChange={() => {}} />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});

describe("MatchColumns", () => {
  // frob:tests web/src/components/MatchItem.tsx::MatchColumns kind="unit"
  it("is a decorative strip that adds no list items", () => {
    const { container } = render(<MatchColumns />);
    expect(container.firstElementChild).toHaveAttribute("aria-hidden", "true");
    expect(screen.queryAllByRole("listitem")).toHaveLength(0);
  });
});
