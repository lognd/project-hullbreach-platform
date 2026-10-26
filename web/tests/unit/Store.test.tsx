import { StrictMode } from "react";
import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { clearSession, saveSession } from "@/auth/session";
import { Store } from "@/pages/Store";
import { meFixture } from "../fixtures/me";
import { filterCatalog, makeCatalog } from "../fixtures/store";
import { overflowRisks } from "../support/layout";

/** A JSON Response, as the server would send it. */
function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

/** Signs in as the fixture player (balance 450 on GET /me). */
function signIn(): void {
  saveSession({ token: "tok-1", userId: "user-1", username: "flagship", role: "player" });
}

/** Stubs fetch with one handler per "METHOD path"; unknown routes fail the test loudly. */
function stubApi(routes: Record<string, () => Response>) {
  const mock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const key = `${init?.method ?? "GET"} ${String(input)}`;
    const handler = routes[key];
    if (handler === undefined) {
      throw new Error(`unexpected request ${key}`);
    }
    return handler();
  });
  vi.stubGlobal("fetch", mock);
  return mock;
}

const catalog = makeCatalog(6, ["item-1"]);

/** The Balance readout's value text. */
function balanceText(): string | null {
  return screen.getByText("Balance").parentElement?.querySelector("dd")?.textContent ?? null;
}

beforeEach(() => {
  clearSession();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  clearSession();
});

describe("Store page: browsing", () => {
  // frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("shows name, preview, price and owned flag for every item", async () => {
    stubApi({ "GET /api/v1/catalog": () => jsonResponse(catalog) });
    render(<Store />);

    expect(await screen.findByText("Skin 0")).toBeInTheDocument();
    expect(screen.getAllByRole("listitem")).toHaveLength(6);
    expect(screen.getByAltText("Preview of Skin 0")).toHaveAttribute(
      "src",
      "/previews/item-0.png",
    );
    expect(screen.queryByAltText("Preview of Skin 1")).not.toBeInTheDocument();
    expect(screen.getByText("105")).toBeInTheDocument();
    const owned = screen.getByText("Skin 1").closest("li");
    expect(within(owned as HTMLElement).getByText("Owned")).toBeInTheDocument();
    expect(screen.getAllByText("Owned")).toHaveLength(1);
  });

  // frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("renders only the selected category's items when a tab is pressed", async () => {
    const user = userEvent.setup();
    const fetchMock = stubApi({
      "GET /api/v1/catalog": () => jsonResponse(catalog),
      "GET /api/v1/catalog?category=hulls": () =>
        jsonResponse(filterCatalog(catalog, "hulls")),
    });
    render(<Store />);
    await screen.findByText("Skin 0");

    await user.click(screen.getByRole("button", { name: "hulls" }));

    expect(await screen.findByRole("button", { name: "hulls", pressed: true })).toBeInTheDocument();
    await vi.waitFor(() => expect(screen.getAllByRole("listitem")).toHaveLength(2));
    expect(screen.getByText("Skin 1")).toBeInTheDocument();
    expect(screen.getByText("Skin 4")).toBeInTheDocument();
    expect(screen.queryByText("Skin 0")).not.toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(2);
    // Every category stays available after filtering.
    expect(screen.getByRole("button", { name: "trails" })).toBeInTheDocument();
  });

  // frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("offers a log-in prompt instead of Buy to a signed-out visitor", async () => {
    stubApi({ "GET /api/v1/catalog": () => jsonResponse(catalog) });
    render(<Store />);
    await screen.findByText("Skin 0");

    expect(screen.queryByRole("button", { name: /^Buy/ })).not.toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Log in to buy" })).not.toHaveLength(0);
    expect(screen.getByRole("link", { name: "Log in" })).toHaveAttribute("href", "/login");
    expect(screen.queryByText("Balance")).not.toBeInTheDocument();
  });

  // frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("shows a loading line first, then an empty state for an empty category", async () => {
    stubApi({
      "GET /api/v1/catalog": () => jsonResponse({ items: [], categories: ["hulls"] }),
    });
    render(<Store />);
    expect(screen.getByText(/Loading store/)).toBeInTheDocument();
    expect(await screen.findByText("Nothing in this category yet.")).toBeInTheDocument();
  });

  // frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("reports a failed load and recovers on Try again", async () => {
    const user = userEvent.setup();
    let calls = 0;
    stubApi({
      "GET /api/v1/catalog": () =>
        ++calls === 1 ? jsonResponse({ detail: "catalog unavailable" }, 503) : jsonResponse(catalog),
    });
    render(<Store />);

    expect(await screen.findByRole("alert")).toHaveTextContent("catalog unavailable");
    await user.click(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findByText("Skin 0")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  // frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("sends the token so the server can flag owned items, under StrictMode", async () => {
    signIn();
    const fetchMock = stubApi({
      "GET /api/v1/catalog": () => jsonResponse(catalog),
      "GET /api/v1/me": () => jsonResponse(meFixture),
    });
    render(
      <StrictMode>
        <Store />
      </StrictMode>,
    );
    await screen.findByText("Skin 0");
    const catalogCall = fetchMock.mock.calls.find(([url]) => String(url) === "/api/v1/catalog");
    expect((catalogCall?.[1]?.headers as Record<string, string>).Authorization).toBe(
      "Bearer tok-1",
    );
    await vi.waitFor(() => expect(balanceText()).toBe("450"));
  });

  // frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("has no layout overflow risks at 390 px", async () => {
    signIn();
    stubApi({
      "GET /api/v1/catalog": () => jsonResponse(catalog),
      "GET /api/v1/me": () => jsonResponse(meFixture),
    });
    const { container } = render(<Store />);
    await screen.findByText("Skin 0");
    expect(overflowRisks(container, 390)).toEqual([]);
  });
});

describe("Store page: buying", () => {
  /** Signs in and renders the store with GET /me at balance 450 plus the extra routes. */
  async function renderSignedIn(extra: Record<string, () => Response>) {
    signIn();
    const fetchMock = stubApi({
      "GET /api/v1/catalog": () => jsonResponse(catalog),
      "GET /api/v1/me": () => jsonResponse(meFixture),
      ...extra,
    });
    render(<Store />);
    await screen.findByText("Skin 0");
    await vi.waitFor(() => expect(balanceText()).toBe("450"));
    return fetchMock;
  }

  // frob:ticket 01M2H5T129NG0XCDSDSKV6PFT9
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("asks to confirm, and Cancel backs out without a request", async () => {
    const user = userEvent.setup();
    const fetchMock = await renderSignedIn({});
    const calls = fetchMock.mock.calls.length;

    await user.click(screen.getByRole("button", { name: "Buy Skin 0" }));
    expect(screen.getByText("Spend 100 to buy Skin 0?")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(screen.queryByText("Spend 100 to buy Skin 0?")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Buy Skin 0" })).toBeInTheDocument();
    expect(fetchMock.mock.calls.length).toBe(calls);
  });

  // frob:ticket 01M2H5T129NG0XCDSDSKV6PFT9
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("posts the purchase, marks the item owned and updates the balance", async () => {
    const user = userEvent.setup();
    let meCalls = 0;
    const fetchMock = await renderSignedIn({
      "POST /api/v1/store/purchase": () =>
        jsonResponse({
          item: { ...catalog.items[0], acquired_at: "2026-10-26T00:00:00Z" },
          balance: 350,
        }),
      "GET /api/v1/me": () => jsonResponse({ ...meFixture, currency: ++meCalls > 1 ? 350 : 450 }),
    });

    await user.click(screen.getByRole("button", { name: "Buy Skin 0" }));
    await user.click(screen.getByRole("button", { name: "Confirm purchase of Skin 0" }));

    await vi.waitFor(() => expect(balanceText()).toBe("350"));
    const card = screen.getByText("Skin 0").closest("li") as HTMLElement;
    expect(within(card).getByText("Owned")).toBeInTheDocument();
    expect(within(card).queryByRole("button")).not.toBeInTheDocument();
    const post = fetchMock.mock.calls.find(([, init]) => init?.method === "POST");
    expect(JSON.parse(String(post?.[1]?.body))).toEqual({ item_id: "item-0" });
    expect((post?.[1]?.headers as Record<string, string>).Authorization).toBe("Bearer tok-1");
  });

  // frob:ticket 01M2H5T129NG0XCDSDSKV6PFT9
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("shows the refusal reason and leaves the balance unchanged on 402", async () => {
    const user = userEvent.setup();
    await renderSignedIn({
      "POST /api/v1/store/purchase": () =>
        jsonResponse({ detail: "insufficient funds: price 100, balance 50" }, 402),
    });

    await user.click(screen.getByRole("button", { name: "Buy Skin 0" }));
    await user.click(screen.getByRole("button", { name: "Confirm purchase of Skin 0" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "insufficient funds: price 100, balance 50",
    );
    expect(balanceText()).toBe("450");
    expect(screen.getAllByText("Owned")).toHaveLength(1);
    expect(screen.getByRole("button", { name: "Buy Skin 0" })).toBeInTheDocument();
  });

  // frob:ticket 01M2H5T129NG0XCDSDSKV6PFT9
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("explains a 404 and offers the item no more purchases", async () => {
    const user = userEvent.setup();
    await renderSignedIn({
      "POST /api/v1/store/purchase": () => jsonResponse({ detail: "unknown item" }, 404),
    });
    await user.click(screen.getByRole("button", { name: "Buy Skin 0" }));
    await user.click(screen.getByRole("button", { name: "Confirm purchase of Skin 0" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "This item is no longer in the catalog.",
    );
    expect(balanceText()).toBe("450");
  });

  // frob:ticket 01M2H5T129NG0XCDSDSKV6PFT9
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("says the item is already owned on 409 and marks it owned", async () => {
    const user = userEvent.setup();
    await renderSignedIn({
      "POST /api/v1/store/purchase": () => jsonResponse({ detail: "already owned" }, 409),
    });
    await user.click(screen.getByRole("button", { name: "Buy Skin 0" }));
    await user.click(screen.getByRole("button", { name: "Confirm purchase of Skin 0" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("You already own this item.");
    const card = screen.getByText("Skin 0").closest("li") as HTMLElement;
    expect(within(card).getByText("Owned")).toBeInTheDocument();
    expect(balanceText()).toBe("450");
  });

  // frob:ticket 01M2H5T129NG0XCDSDSKV6PFT9
  // frob:tests web/src/pages/Store.tsx::Store kind="unit"
  it("tells the player to log in again on 401 and on any other failure gives a generic line", async () => {
    const user = userEvent.setup();
    let status = 401;
    await renderSignedIn({
      "POST /api/v1/store/purchase": () => jsonResponse({ detail: "nope" }, status),
    });
    await user.click(screen.getByRole("button", { name: "Buy Skin 0" }));
    await user.click(screen.getByRole("button", { name: "Confirm purchase of Skin 0" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Your session has expired. Log in again to buy.",
    );

    status = 500;
    await user.click(screen.getByRole("button", { name: "Buy Skin 0" }));
    await user.click(screen.getByRole("button", { name: "Confirm purchase of Skin 0" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Something went wrong. Please try again.",
    );
    expect(balanceText()).toBe("450");
  });
});
