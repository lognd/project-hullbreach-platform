import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { SkinPicker } from "@/components/SkinPicker";
import { meFixture } from "../fixtures/me";

/** A JSON Response, as the server would send it. */
function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("SkinPicker", () => {
  // frob:tests web/src/components/SkinPicker.tsx::SkinPicker kind="unit"
  // frob:tests web/src/api/me.ts::equipSkin kind="unit"
  it("equips the pressed skin and marks it", async () => {
    const [ember] = meFixture.inventory;
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(ember));
    vi.stubGlobal("fetch", fetchMock);
    render(<SkinPicker token="tok-1" skins={meFixture.inventory} initial={null} />);

    await userEvent.click(screen.getByRole("button", { name: "Ember Hull" }));

    expect(
      await screen.findByRole("button", { name: "Ember Hull (equipped)" }),
    ).toHaveAttribute("aria-pressed", "true");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/me/equipped",
      expect.objectContaining({
        method: "PUT",
        body: JSON.stringify({ item_id: ember.id }),
      }),
    );
  });

  // frob:tests web/src/components/SkinPicker.tsx::SkinPicker kind="unit"
  it("starts with the server's equipped skin pressed", () => {
    render(
      <SkinPicker
        token="tok-1"
        skins={meFixture.inventory}
        initial={meFixture.inventory[1]}
      />,
    );

    expect(
      screen.getByRole("button", { name: "Frost Plating (equipped)" }),
    ).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "Ember Hull" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
  });

  // frob:tests web/src/components/SkinPicker.tsx::SkinPicker kind="unit"
  it("shows a refusal as an alert and keeps the old skin", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ detail: "item not owned" }, 403)),
    );
    render(
      <SkinPicker
        token="tok-1"
        skins={meFixture.inventory}
        initial={meFixture.inventory[1]}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "Ember Hull" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("item not owned");
    expect(
      screen.getByRole("button", { name: "Frost Plating (equipped)" }),
    ).toHaveAttribute("aria-pressed", "true");
  });

  // frob:ticket 01M5XYWVF56BWJXQ43EBP9FP8F
  // frob:tests web/src/components/SkinPicker.tsx::SkinPicker kind="unit"
  // frob:tests web/src/api/me.ts::unequipSkin kind="unit"
  it("unequips the equipped skin when it is pressed again", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);
    render(
      <SkinPicker
        token="tok-1"
        skins={meFixture.inventory}
        initial={meFixture.inventory[1]}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "Frost Plating (equipped)" }));

    expect(await screen.findByRole("button", { name: "Frost Plating" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
    expect(screen.queryByText(/equipped\)/)).toBeNull();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/me/equipped",
      expect.objectContaining({ method: "DELETE" }),
    );
  });

  // frob:ticket 01M5XYWVF56BWJXQ43EBP9FP8F
  // frob:tests web/src/components/SkinPicker.tsx::SkinPicker kind="unit"
  it("shows an unequip failure as an alert and keeps the skin pressed", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ detail: "could not unequip" }, 500)),
    );
    render(
      <SkinPicker
        token="tok-1"
        skins={meFixture.inventory}
        initial={meFixture.inventory[1]}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "Frost Plating (equipped)" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("could not unequip");
    expect(
      screen.getByRole("button", { name: "Frost Plating (equipped)" }),
    ).toHaveAttribute("aria-pressed", "true");
  });
});
