import type { ReactNode } from "react";

/** Border color per Panel tone: hairline for ordinary panels, cyan for the one panel a page is about. */
const PANEL_TONE = {
  quiet: "border-line",
  primary: "border-accent",
} as const;

/** Which border a Panel draws. */
export type PanelTone = keyof typeof PANEL_TONE;

// frob:doc docs/index.md#visual-design-rules
/** A square, hairline-bordered panel; `label` sets a mono caption into the top border and `tone="primary"` draws the cyan border. The one container for forms, charts, stats and empty states. */
export function Panel({
  className,
  label,
  tone = "quiet",
  children,
}: {
  className?: string;
  label?: string;
  tone?: PanelTone;
  children: ReactNode;
}) {
  return (
    <div className={`relative border bg-panel ${PANEL_TONE[tone]} ${className ?? ""}`}>
      {label !== undefined ? (
        <span className="absolute -top-space-8 left-space-12 bg-paper px-space-8 font-mono text-font-size-12 uppercase leading-none tracking-widest text-muted">
          {label}
        </span>
      ) : null}
      {children}
    </div>
  );
}

// frob:doc docs/index.md#visual-design-rules
/** A section's h2 in the display face, so every page's sections share one heading style. */
export function SectionHeading({ id, children }: { id: string; children: ReactNode }) {
  return (
    <h2
      id={id}
      className="font-display text-font-size-16 font-normal uppercase tracking-wider text-ink"
    >
      {children}
    </h2>
  );
}

/** Text color per StatTile tone; plain numbers stay ink, `signal` is reserved for the ELO rating, wins read cyan and losses orange. */
const STAT_TONE = {
  plain: "text-ink",
  accent: "text-accent",
  signal: "text-signal",
  ok: "text-accent",
  fail: "text-signal",
} as const;

/** How a StatTile value is colored. */
export type StatTone = keyof typeof STAT_TONE;

// frob:doc docs/index.md#visual-design-rules
/** One stat inside a `<dl>`: a small mono label over a tabular numeral; `size="large"` is the single hero number of a page. */
export function StatTile({
  label,
  value,
  tone = "plain",
  size = "small",
}: {
  label: string;
  value: string | number;
  tone?: StatTone;
  size?: "small" | "large";
}) {
  return (
    <div className="flex flex-col gap-space-4">
      <dt className="font-mono text-font-size-12 uppercase tracking-widest text-muted">
        {label}
      </dt>
      <dd
        className={`font-mono font-semibold tabular-nums ${size === "large" ? "text-font-size-64" : "text-font-size-24"} ${STAT_TONE[tone]}`}
      >
        {value}
      </dd>
    </div>
  );
}

// frob:doc docs/index.md#visual-design-rules
/** An empty list: `title` says what is missing, `hint` says what the panel will show, and `action` is the one concrete next step. */
export function EmptyState({
  title,
  hint,
  action,
}: {
  title: string;
  hint: string;
  action?: ReactNode;
}) {
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
    <div aria-hidden="true" className="flex flex-col gap-space-8">
      {Array.from({ length: count }, (_, index) => (
        <div key={index} className="h-space-48 border border-line bg-panel" />
      ))}
    </div>
  );
}
