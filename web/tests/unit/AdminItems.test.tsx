import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { clearSession, saveSession } from "@/auth/session";
import { AdminItems } from "@/pages/admin/Items";

/** A JSON Response, as the server would send it. */
function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

const ITEM = {
  id: "i1",
  slug: "paint",
  name: "Paint",
  category: "cosmetic",
  price: 100,
  preview_url: null,
  retired: false,
};

beforeEach(() => {
  clearSession();
  window.history.pushState({}, "", "/admin/items");
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  clearSession();
});

describe("AdminItems page", () => {
  // frob:tests web/src/pages/admin/Items.tsx::AdminItems kind="unit"
  it("saves a changed price through PATCH and shows the item", async () => {
    saveSession({ token: "adm", userId: "a", username: "root", role: "admin" });
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse([ITEM]))
      .mockResolvedValueOnce(jsonResponse({ ...ITEM, price: 250 }));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<AdminItems />);

    const price = await screen.findByLabelText("Price for Paint");
    await user.clear(price);
    await user.type(price, "250");
    await user.click(screen.getByRole("button", { name: "Save Paint" }));

    await vi.waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(2);
    });
    expect(fetchMock.mock.calls[1]?.[0]).toBe("/api/v1/admin/items/i1");
    const init = fetchMock.mock.calls[1]?.[1] as RequestInit;
    expect(init.method).toBe("PATCH");
    expect(JSON.parse(init.body as string)).toEqual({ price: 250 });
  });

  // frob:tests web/src/pages/admin/Items.tsx::AdminItems kind="unit"
  it("redirects a non-admin away", () => {
    saveSession({ token: "t", userId: "u", username: "pilot", role: "player" });
    vi.stubGlobal("fetch", vi.fn());
    render(<AdminItems />);
    expect(window.location.pathname).toBe("/");
  });
});
