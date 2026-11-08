import { useEffect, useState } from "react";
import { listItems, patchItem, retireItem, type AdminItem } from "@/api/admin";
import { ApiError } from "@/api/auth";
import { Button } from "@/components/Button";
import { Notice } from "@/components/Notice";
import { Page } from "@/components/Page";
import { AdminGate } from "@/pages/admin/AdminGate";

/** Editable list of catalog items for one admin token. */
function ItemsBody({ token }: { token: string }) {
  const [items, setItems] = useState<AdminItem[]>([]);
  const [prices, setPrices] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listItems(token)
      .then(setItems)
      .catch((e: unknown) => {
        setError(e instanceof ApiError ? e.detail : "Could not load items.");
      });
  }, [token]);

  function replace(updated: AdminItem): void {
    setItems((previous) => previous.map((i) => (i.id === updated.id ? updated : i)));
  }
  async function save(item: AdminItem): Promise<void> {
    setError(null);
    try {
      replace(await patchItem(token, item.id, { price: Number(prices[item.id]) }));
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Could not save.");
    }
  }
  async function retire(item: AdminItem): Promise<void> {
    setError(null);
    try {
      replace(await retireItem(token, item.id));
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Could not retire.");
    }
  }

  return (
    <Page
      crumbs={[{ label: "Admin" }, { label: "Items" }]}
      title="Items"
      purpose="Change an item's price or retire it. Owners keep retired items."
    >
      {error !== null ? (
        <Notice tone="error" role="alert">
          {error}
        </Notice>
      ) : null}
      <ul className="flex flex-col gap-space-8">
        {items.map((item) => (
          <li key={item.id} className="flex items-center gap-space-12">
            <span>
              {item.name}
              {item.retired ? " (retired)" : ""}
            </span>
            <label>
              {`Price for ${item.name}`}
              <input
                type="number"
                min={0}
                value={prices[item.id] ?? String(item.price)}
                onChange={(event) => {
                  setPrices({ ...prices, [item.id]: event.target.value });
                }}
              />
            </label>
            <Button
              onClick={() => {
                void save(item);
              }}
            >
              {`Save ${item.name}`}
            </Button>
            <Button
              disabled={item.retired}
              onClick={() => {
                void retire(item);
              }}
            >
              {`Retire ${item.name}`}
            </Button>
          </li>
        ))}
      </ul>
    </Page>
  );
}

// frob:ticket 01M2H5T12E0JWYSBMM6HZ09J6Q
/** Admin item editor: edit prices and retire items; non-admins are redirected away. */
export function AdminItems() {
  return <AdminGate>{(token) => <ItemsBody token={token} />}</AdminGate>;
}
