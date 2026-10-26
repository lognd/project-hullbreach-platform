import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Footer } from "@/components/Footer";
import { PolicySection } from "@/components/PolicySection";
import { DataPolicy } from "@/pages/DataPolicy";

afterEach(cleanup);

describe("DataPolicy", () => {
  // frob:tests web/src/pages/DataPolicy.tsx::DataPolicy kind="unit"
  it("has sections for stored data, purpose and deletion", () => {
    render(<DataPolicy />);
    for (const name of ["Stored data", "Purpose", "Deletion"]) {
      expect(screen.getByRole("heading", { level: 2, name })).toBeInTheDocument();
    }
    expect(
      screen.getByRole("heading", { level: 1, name: "Data policy" }),
    ).toBeInTheDocument();
  });

  // frob:tests web/src/pages/DataPolicy.tsx::DataPolicy kind="unit"
  it("names the fields the server really stores", () => {
    render(<DataPolicy />);
    expect(screen.getByText(/username and email address/i)).toBeInTheDocument();
    expect(screen.getByText(/hash of your password/i)).toBeInTheDocument();
  });

  // frob:tests web/src/components/Footer.tsx::Footer kind="unit"
  it("is the target of the footer link", () => {
    render(<Footer />);
    expect(screen.getByRole("link", { name: "Data policy" })).toHaveAttribute(
      "href",
      "/data-policy",
    );
  });

  // frob:tests web/src/components/PolicySection.tsx::PolicySection kind="unit"
  it("labels a policy section by its heading", () => {
    render(
      <PolicySection id="x" title="Title">
        <p>Body</p>
      </PolicySection>,
    );
    expect(screen.getByRole("region", { name: "Title" })).toHaveTextContent("Body");
  });
});
