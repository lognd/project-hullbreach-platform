import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "@/api/auth";
import { fetchMe } from "@/api/me";
import { fetchCatalog, purchaseItem, type Catalog, type CatalogItem } from "@/api/store";
import { useSession } from "@/auth/session";
import { Button, ButtonLink } from "@/components/Button";
import { ItemCard, type BuyPhase } from "@/components/ItemCard";
import { Loading, Notice } from "@/components/Notice";
import { Page } from "@/components/Page";
import { EmptyState, SkeletonRows, StatTile } from "@/components/Readout";

/** Shown for any failure the server did not explain. */
const GENERIC_ERROR = "Something went wrong. Please try again.";

/** The one purchase in progress: which item and whether it awaits confirmation or is in flight. */
type Pending = { itemId: string; phase: Exclude<BuyPhase, "idle"> };

/** What the page knows about the catalog: the items shown, every category, the in-flight flag and the last failure. */
type CatalogState = {
  catalog: Catalog | null;
  loading: boolean;
  error: string | null;
};

const INITIAL: CatalogState = { catalog: null, loading: false, error: null };

// frob:ticket 01M2H5T129NG0XCDSDSKV6PFT9
// frob:doc docs/index.md#store-page
/** Maps a refused purchase to the message the player sees; 402 keeps the server's price-and-balance text. */
export function purchaseErrorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return GENERIC_ERROR;
  }
  switch (error.status) {
    case 402:
      return error.detail;
    case 404:
      return "This item is no longer in the catalog.";
    case 409:
      return "You already own this item.";
    case 401:
      return "Your session has expired. Log in again to buy.";
    default:
      return GENERIC_ERROR;
  }
}

// frob:ticket 01M2H5T1242JFMB5A03JSDP5KP
// frob:doc docs/index.md#store-page
/** Store page: browse the public catalog by category, and (signed in) buy items with a confirm step and per-status errors. */
export function Store() {
  const session = useSession();
  const token = session?.token ?? null;
  const [category, setCategory] = useState<string | null>(null);
  const [state, setState] = useState<CatalogState>(INITIAL);
  const [balance, setBalance] = useState<number | null>(null);
  const [pending, setPending] = useState<Pending | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  // Bumped when a catalog load restarts or the page unmounts, so stale responses are dropped.
  const generation = useRef(0);

  const load = useCallback(async (): Promise<void> => {
    const mine = generation.current;
    setState((previous) => ({ ...previous, loading: true, error: null }));
    try {
      const catalog = await fetchCatalog(token, category);
      if (generation.current !== mine) {
        return;
      }
      setState({ catalog, loading: false, error: null });
    } catch (error) {
      if (generation.current !== mine) {
        return;
      }
      setState((previous) => ({
        ...previous,
        loading: false,
        error: error instanceof ApiError ? error.detail : GENERIC_ERROR,
      }));
    }
  }, [token, category]);

  useEffect(() => {
    generation.current += 1;
    setPending(null);
    setErrors({});
    void load();
    return () => {
      generation.current += 1;
    };
  }, [load]);

  // Balance follows the session; a failed read leaves it unknown ("--") rather than blocking the store.
  useEffect(() => {
    if (token === null) {
      setBalance(null);
      return;
    }
    let live = true;
    fetchMe(token)
      .then((me) => {
        if (live) {
          setBalance(me.currency);
        }
      })
      .catch(() => {
        if (live) {
          setBalance(null);
        }
      });
    return () => {
      live = false;
    };
  }, [token]);

  // Flags one item owned in the loaded catalog without a refetch.
  const markOwned = useCallback((itemId: string): void => {
    setState((previous) =>
      previous.catalog === null
        ? previous
        : {
            ...previous,
            catalog: {
              ...previous.catalog,
              items: previous.catalog.items.map((entry) =>
                entry.id === itemId ? { ...entry, owned: true } : entry,
              ),
            },
          },
    );
  }, []);

  const confirm = useCallback(
    async (item: CatalogItem): Promise<void> => {
      if (token === null) {
        return;
      }
      setPending({ itemId: item.id, phase: "buying" });
      setErrors((previous) => ({ ...previous, [item.id]: "" }));
      try {
        const receipt = await purchaseItem(token, item.id);
        setBalance(receipt.balance);
        markOwned(item.id);
        setPending(null);
        // Reconcile with the server's view; a failure keeps the receipt's balance.
        fetchMe(token)
          .then((me) => setBalance(me.currency))
          .catch(() => undefined);
      } catch (error) {
        if (error instanceof ApiError && error.status === 409) {
          markOwned(item.id);
        }
        setErrors((previous) => ({ ...previous, [item.id]: purchaseErrorMessage(error) }));
        setPending(null);
      }
    },
    [token, markOwned],
  );

  const { catalog, loading, error } = state;
  const signedIn = session !== null;

  return (
    <Page
      crumbs={[{ label: "Store" }]}
      title="Store"
      purpose="Spend your currency on cosmetic skins. Every item is cosmetic only."
      width="wide"
    >
      {signedIn ? (
        <dl className="max-w-xs">
          <StatTile label="Balance" value={balance === null ? "--" : String(balance)} />
        </dl>
      ) : (
        <Notice tone="info">
          <span>Browse freely. Log in to buy items and see which ones you own.</span>
          <ButtonLink href="/login" variant="primary">
            Log in
          </ButtonLink>
        </Notice>
      )}
      {catalog !== null ? (
        <div role="group" aria-label="Categories" className="flex flex-wrap gap-space-8">
          {[null, ...catalog.categories].map((name) => (
            <Button
              key={name ?? "all"}
              variant="secondary"
              aria-pressed={category === name}
              className={category === name ? "border-ink bg-panel" : ""}
              onClick={() => setCategory(name)}
            >
              {name ?? "All"}
            </Button>
          ))}
        </div>
      ) : null}
      {catalog !== null && catalog.items.length === 0 ? (
        <EmptyState
          title="Nothing in this category yet."
          hint="Pick another category to keep browsing."
        />
      ) : null}
      {catalog !== null && catalog.items.length > 0 ? (
        <ul className="grid grid-cols-1 gap-space-16 sm:grid-cols-2 lg:grid-cols-3">
          {catalog.items.map((item) => {
            const mine = pending?.itemId === item.id;
            return (
              <ItemCard
                key={item.id}
                item={item}
                buy={
                  signedIn
                    ? {
                        phase: mine ? pending.phase : "idle",
                        error: errors[item.id] || null,
                        onBuy: () => {
                          setErrors((previous) => ({ ...previous, [item.id]: "" }));
                          setPending({ itemId: item.id, phase: "confirm" });
                        },
                        onConfirm: () => {
                          void confirm(item);
                        },
                        onCancel: () => setPending(null),
                      }
                    : null
                }
              />
            );
          })}
        </ul>
      ) : null}
      {loading && catalog === null ? (
        <>
          <Loading label="Loading store" />
          <SkeletonRows count={6} />
        </>
      ) : null}
      {error !== null ? (
        <Notice tone="error" role="alert">
          <span>{error}</span>
          <Button
            variant="primary"
            disabled={loading}
            onClick={() => {
              void load();
            }}
          >
            Try again
          </Button>
        </Notice>
      ) : null}
    </Page>
  );
}
