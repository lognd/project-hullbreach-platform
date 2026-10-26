import type { ReactNode } from "react";

/** What a notice reports: a failure, a success, or neutral information. */
export type NoticeTone = "error" | "ok" | "info";

/** Left-edge color per tone: errors take the reserved signal orange, success the cyan line, info a quiet hairline. */
const EDGE: Record<NoticeTone, string> = {
  error: "border-signal",
  ok: "border-accent",
  info: "border-line",
};

/** Mono lead word per tone, so a notice never relies on color alone. */
const LEAD: Record<NoticeTone, string> = { error: "Error", ok: "Done", info: "Note" };

// frob:doc docs/index.md#visual-design-rules
/** A message strip with a colored left edge; `role` is alert for errors and status for success so screen readers announce it. */
export function Notice({
  tone,
  role,
  id,
  children,
}: {
  tone: NoticeTone;
  role?: "alert" | "status";
  id?: string;
  children: ReactNode;
}) {
  return (
    <div
      id={id}
      role={role}
      className={`flex flex-wrap items-center gap-x-space-12 gap-y-space-8 border border-l-4 bg-panel px-space-16 py-space-12 text-font-size-14 text-ink ${EDGE[tone]}`}
    >
      <span className="font-mono text-font-size-12 font-semibold uppercase tracking-widest text-muted">
        {LEAD[tone]}
      </span>
      <div className="flex min-w-0 flex-1 flex-wrap items-center justify-between gap-x-space-12 gap-y-space-8 wrap-anywhere">
        {children}
      </div>
    </div>
  );
}

// frob:doc docs/index.md#visual-design-rules
/** The loading line every data page shows while its first request is in flight; a static mono readout, so there is nothing to animate. */
export function Loading({ label }: { label: string }) {
  return (
    <p
      role="status"
      aria-live="polite"
      className="font-mono text-font-size-14 uppercase tracking-wider text-muted"
    >
      {label}
      <span aria-hidden="true">...</span>
    </p>
  );
}
