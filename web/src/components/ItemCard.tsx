import type { CatalogItem } from "@/api/store";
import { Button, ButtonLink } from "@/components/Button";
import { Notice } from "@/components/Notice";

/** Where a card's purchase flow stands: nothing started, asking to confirm, or the request in flight. */
export type BuyPhase = "idle" | "confirm" | "buying";

/** What the card needs from the page to run the buy flow; absent while the player is signed out. */
export type BuyControls = {
  phase: BuyPhase;
  error: string | null;
  onBuy: () => void;
  onConfirm: () => void;
  onCancel: () => void;
};

// frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
// frob:doc docs/index.md#store-page
/** The preview image, or a bordered placeholder carrying the category initial when the item has none. */
function Preview({ item }: { item: CatalogItem }) {
  if (item.preview_url !== null) {
    return (
      <img
        src={item.preview_url}
        alt={`Preview of ${item.name}`}
        loading="lazy"
        className="aspect-video w-full border border-line bg-paper object-cover"
      />
    );
  }
  return (
    <div
      aria-hidden="true"
      className="flex aspect-video w-full items-center justify-center border border-line bg-paper font-display text-font-size-24 uppercase text-muted"
    >
      {item.category.slice(0, 1)}
    </div>
  );
}

// frob:ticket 01M2H5T129NG0XCDSDSKV6PFT9
// frob:doc docs/index.md#store-page
/** The action row: Log in when signed out, an Owned tag when owned, otherwise Buy and its confirm step. */
function Actions({ item, buy }: { item: CatalogItem; buy: BuyControls | null }) {
  if (item.owned) {
    return null;
  }
  if (buy === null) {
    return (
      <ButtonLink href="/login" variant="secondary">
        Log in to buy
      </ButtonLink>
    );
  }
  if (buy.phase === "idle") {
    return (
      <Button variant="secondary" onClick={buy.onBuy} aria-label={`Buy ${item.name}`}>
        Buy
      </Button>
    );
  }
  return (
    <div className="flex flex-col gap-space-8">
      <p className="font-mono text-font-size-14 text-ink wrap-anywhere">
        Spend {item.price} to buy {item.name}?
      </p>
      <div className="flex flex-wrap gap-space-8">
        <Button
          variant="primary"
          disabled={buy.phase === "buying"}
          onClick={buy.onConfirm}
          aria-label={`Confirm purchase of ${item.name}`}
        >
          {buy.phase === "buying" ? "Buying" : "Confirm"}
        </Button>
        <Button variant="secondary" disabled={buy.phase === "buying"} onClick={buy.onCancel}>
          Cancel
        </Button>
      </div>
    </div>
  );
}

// frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
// frob:doc docs/index.md#store-page
/** One catalog card: preview, name, category, price, an Owned tag, and the buy flow (null `buy` means signed out). */
export function ItemCard({ item, buy }: { item: CatalogItem; buy: BuyControls | null }) {
  return (
    <li className="flex min-w-space-0 flex-col gap-space-12 border border-line bg-panel p-space-16">
      <Preview item={item} />
      <div className="flex min-w-space-0 flex-col gap-space-4">
        <h3 className="font-display text-font-size-16 text-ink wrap-anywhere">{item.name}</h3>
        <p className="font-mono text-font-size-12 uppercase tracking-widest text-muted">
          {item.category}
        </p>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-space-8">
        <span className="font-mono text-font-size-16 font-semibold tabular-nums text-ink">
          {item.price}
        </span>
        {item.owned ? (
          <span className="border border-accent px-space-8 py-space-4 font-mono text-font-size-12 uppercase tracking-widest text-accent">
            Owned
          </span>
        ) : null}
      </div>
      <Actions item={item} buy={buy} />
      {buy?.error != null ? (
        <Notice tone="error" role="alert">
          <span>{buy.error}</span>
        </Notice>
      ) : null}
    </li>
  );
}
