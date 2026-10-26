import type { Catalog, CatalogItem } from "@/api/store";

/** Every category the fixture catalog knows, in the server's order. */
export const CATEGORIES = ["decals", "hulls", "trails"];

/** Builds a deterministic catalog item; `index` fixes id, name and price, `category` and `owned` override. */
export function makeItem(
  index: number,
  category = CATEGORIES[index % CATEGORIES.length] ?? "hulls",
  owned = false,
): CatalogItem {
  return {
    id: `item-${index}`,
    slug: `item-${index}`,
    name: `Skin ${index}`,
    category,
    price: 100 + index,
    preview_url: index % 2 === 0 ? `/previews/item-${index}.png` : null,
    owned,
  };
}

/** A typed GET /api/v1/catalog body of `count` items (all categories) with `ownedIds` flagged owned. */
export function makeCatalog(count: number, ownedIds: readonly string[] = []): Catalog {
  return {
    items: Array.from({ length: count }, (_, index) =>
      makeItem(index, undefined, ownedIds.includes(`item-${index}`)),
    ),
    categories: CATEGORIES,
  };
}

/** The same catalog filtered to one category, as GET /api/v1/catalog?category= answers. */
export function filterCatalog(catalog: Catalog, category: string): Catalog {
  return { ...catalog, items: catalog.items.filter((item) => item.category === category) };
}
