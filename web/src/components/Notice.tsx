import type { ReactNode } from "react";

/** What a notice reports: a failure, a success, or neutral information. */
export type NoticeTone = "error" | "ok" | "info";

/** Left-edge color per tone, matching the in-game hull-stress colors. */
const EDGE: Record<NoticeTone, string> = {
  error: "border-stress-fail text-stress-fail",
  ok: "border-stress-ok text-stress-ok",
  info: "border-line text-muted",
};

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
      className={`flex flex-wrap items-center justify-between gap-space-12 border-l-4 bg-panel px-space-16 py-space-12 text-font-size-14 ${EDGE[tone]}`}
    >
      {children}
    </div>
  );
}

// frob:doc docs/index.md#visual-design-rules
/** The loading line every data page shows while its first request is in flight. */
export function Loading({ label }: { label: string }) {
  return (
    <p role="status" aria-live="polite" className="font-mono text-font-size-14 uppercase tracking-wider text-muted">
      {label}
    </p>
  );
}
