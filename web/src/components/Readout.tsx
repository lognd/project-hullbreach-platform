import type { ReactNode } from "react";

// frob:doc docs/index.md#visual-design-rules
/** A hairline-bordered panel with HUD corner brackets (top-left, bottom-right); the one container for forms, stat tiles and empty states. */
export function Panel({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <div className={`relative border border-line bg-panel ${className ?? ""}`}>
      <span aria-hidden="true" className="absolute -left-px -top-px h-space-8 w-space-8 border-l-2 border-t-2 border-accent" />
      <span aria-hidden="true" className="absolute -bottom-px -right-px h-space-8 w-space-8 border-b-2 border-r-2 border-accent" />
      {children}
    </div>
  );
}

/** Text color per StatTile tone; plain numbers stay ink, rating-like numbers take the accent. */
const STAT_TONE = {
  plain: "text-ink",
  accent: "text-accent",
  ok: "text-stress-ok",
  fail: "text-stress-fail",
} as const;

/** How a StatTile value is colored. */
export type StatTone = keyof typeof STAT_TONE;

// frob:doc docs/index.md#visual-design-rules
/** One stat inside a `<dl>`: a small mono label over a large tabular numeral, so numbers line up and read first. */
export function StatTile({ label, value, tone = "plain" }: { label: string; value: string | number; tone?: StatTone }) {
  return (
    <Panel className="flex flex-col gap-space-4 px-space-16 py-space-12">
      <dt className="font-mono text-font-size-12 uppercase tracking-widest text-muted">{label}</dt>
      <dd className={`font-mono text-font-size-32 font-semibold tabular-nums ${STAT_TONE[tone]}`}>{value}</dd>
    </Panel>
  );
}

// frob:doc docs/index.md#visual-design-rules
/** An empty list: `title` says what is missing, `hint` says what the panel will show, and `action` is the one concrete next step. */
export function EmptyState({ title, hint, action }: { title: string; hint: string; action?: ReactNode }) {
  return (
    <Panel className="flex flex-col items-start gap-space-12 px-space-16 py-space-24">
      <p className="text-font-size-16 font-medium text-ink">{title}</p>
      <p className="text-font-size-14 text-muted">{hint}</p>
      {action}
    </Panel>
  );
}

// frob:doc docs/index.md#visual-design-rules
/** Flat placeholder rows shown while a list loads; decorative (aria-hidden) because a Loading status line announces the wait. */
export function SkeletonRows({ count }: { count: number }) {
  return (
    <div aria-hidden="true" className="flex flex-col gap-space-4">
      {Array.from({ length: count }, (_, index) => (
        <div key={index} className="h-space-48 border border-line bg-panel" />
      ))}
    </div>
  );
}
