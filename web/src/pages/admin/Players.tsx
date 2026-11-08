import { useState } from "react";
import {
  fetchPlayer,
  moderatePlayer,
  searchPlayers,
  type AdminPlayer,
  type AdminPlayerDetail,
} from "@/api/admin";
import { ApiError } from "@/api/auth";
import { Button } from "@/components/Button";
import { Notice } from "@/components/Notice";
import { Page } from "@/components/Page";
import { TextField } from "@/components/TextField";
import { AdminGate } from "@/pages/admin/AdminGate";

/** Turns a thrown error into a user-facing sentence. */
function message(error: unknown): string {
  return error instanceof ApiError ? error.detail : "Something went wrong. Please try again.";
}

/** Search, detail, suspend and reinstate for one admin token. */
function PlayersBody({ token }: { token: string }) {
  const [query, setQuery] = useState("");
  const [rows, setRows] = useState<AdminPlayer[] | null>(null);
  const [detail, setDetail] = useState<AdminPlayerDetail | null>(null);
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function search(): Promise<void> {
    setError(null);
    try {
      setRows(await searchPlayers(token, query));
    } catch (e) {
      setError(message(e));
    }
  }
  async function open(id: string): Promise<void> {
    setError(null);
    try {
      setDetail(await fetchPlayer(token, id));
    } catch (e) {
      setError(message(e));
    }
  }
  async function moderate(action: "suspend" | "unsuspend"): Promise<void> {
    if (detail === null) {
      return;
    }
    setError(null);
    try {
      setDetail(await moderatePlayer(token, detail.id, action, reason));
      setReason("");
    } catch (e) {
      setError(message(e));
    }
  }

  return (
    <Page
      crumbs={[{ label: "Admin" }, { label: "Players" }]}
      title="Players"
      purpose="Look up a player, review their record, and suspend or reinstate them."
    >
      <form
        className="flex flex-col gap-space-8"
        onSubmit={(event) => {
          event.preventDefault();
          void search();
        }}
      >
        <TextField id="q" name="q" label="Username" value={query} error={undefined} onChange={setQuery} />
        <Button variant="primary" type="submit">
          Search
        </Button>
      </form>
      {error !== null ? (
        <Notice tone="error" role="alert">
          {error}
        </Notice>
      ) : null}
      {rows !== null ? (
        <ul className="flex flex-col gap-space-4">
          {rows.map((row) => (
            <li key={row.id} className="flex items-center gap-space-12">
              <span>
                {row.username} ({row.rating}){row.suspended ? " suspended" : ""}
              </span>
              <Button
                onClick={() => {
                  void open(row.id);
                }}
              >
                {`Open ${row.username}`}
              </Button>
            </li>
          ))}
        </ul>
      ) : null}
      {detail !== null ? (
        <section aria-label="Player detail" className="flex flex-col gap-space-8">
          <h2 className="text-font-size-20">{detail.username}</h2>
          <p>
            {detail.email} / ELO {detail.rating} / balance {detail.balance}
          </p>
          {detail.suspended ? <p>Suspended: {detail.suspended_reason}</p> : null}
          <h3>Moderation</h3>
          <ul>
            {detail.moderation.map((m) => (
              <li key={m.created_at + m.action}>
                {m.action}: {m.reason}
              </li>
            ))}
          </ul>
          <h3>Trust events</h3>
          <ul>
            {detail.trust_events.map((t) => (
              <li key={t.created_at + t.kind}>
                {t.kind} at {t.created_at}
              </li>
            ))}
          </ul>
          <TextField id="reason" name="reason" label="Reason" value={reason} error={undefined} onChange={setReason} />
          <Button
            variant="primary"
            disabled={reason.trim() === ""}
            onClick={() => {
              void moderate(detail.suspended ? "unsuspend" : "suspend");
            }}
          >
            {detail.suspended ? "Reinstate" : "Suspend"}
          </Button>
        </section>
      ) : null}
    </Page>
  );
}

// frob:ticket 01M2H5T12E0JWYSBMM6HZ09J6Q
/** Admin players page: search, detail, suspend and reinstate; non-admins are redirected away. */
export function AdminPlayers() {
  return <AdminGate>{(token) => <PlayersBody token={token} />}</AdminGate>;
}
