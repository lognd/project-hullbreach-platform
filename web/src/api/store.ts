import { apiFetch, bearerHeaders, errorFromResponse, requestJson } from "@/api/auth";

/** Path of the public catalog endpoint. */
const CATALOG_PATH = "/api/v1/catalog";

/** Path of the purchase endpoint. */
const PURCHASE_PATH = "/api/v1/store/purchase";

// frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
// frob:doc docs/index.md#store-page
/** One catalog entry: what it is, what it costs and whether the caller owns it. */
export type CatalogItem = {
  id: string;
  slug: string;
  name: string;
  category: string;
  price: number;
  preview_url: string | null;
  owned: boolean;
};

// frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
// frob:doc docs/index.md#store-page
/** GET /api/v1/catalog's 200 body: the (filtered) items plus every category name. */
export type Catalog = {
  items: CatalogItem[];
  categories: string[];
};

// frob:ticket 01M2H5T129NG0XCDSDSKV6PFT9
// frob:doc docs/index.md#store-page
/** POST /api/v1/store/purchase's 200 body: the item now owned and the balance after paying. */
export type PurchaseReceipt = {
  item: Pick<CatalogItem, "id" | "slug" | "name" | "category" | "price" | "preview_url"> & {
    acquired_at: string;
  };
  balance: number;
};

// frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
// frob:doc docs/index.md#store-page
/** GET /api/v1/catalog, optionally for one category; public, and a token only sets the owned flags; 503 rejects with an ApiError. */
export async function fetchCatalog(
  token: string | null,
  category: string | null = null,
): Promise<Catalog> {
  const path =
    category === null ? CATALOG_PATH : `${CATALOG_PATH}?category=${encodeURIComponent(category)}`;
  return requestJson<Catalog>(
    path,
    token === null ? undefined : { headers: bearerHeaders(token) },
  );
}

// frob:ticket 01M2H5T129NG0XCDSDSKV6PFT9
// frob:doc docs/index.md#store-page
/** POST /api/v1/store/purchase for one item; 402/404/409/401 reject with an ApiError carrying the server's reason. */
export async function purchaseItem(token: string, itemId: string): Promise<PurchaseReceipt> {
  const response = await apiFetch(PURCHASE_PATH, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...bearerHeaders(token) },
    body: JSON.stringify({ item_id: itemId }),
  });
  if (!response.ok) {
    throw await errorFromResponse(response);
  }
  return (await response.json()) as PurchaseReceipt;
}
