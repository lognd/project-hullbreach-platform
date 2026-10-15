import type { ReactNode } from "react";

/** Content column width: narrow for forms, wide for the landing page and lists. */
export type PageWidth = "form" | "content" | "wide";

/** max-width per PageWidth; every page is left-aligned inside it, never centered text. */
const WIDTH: Record<PageWidth, string> = {
  form: "max-w-[28rem]",
  content: "max-w-[48rem]",
  wide: "max-w-[72rem]",
};

// frob:doc docs/index.md#visual-design-rules
/** The `<main>` every route renders: a left-aligned column with a mono eyebrow label above the h1, so all pages share one rhythm. */
export function Page({
  eyebrow,
  title,
  width = "content",
  titleClassName,
  children,
}: {
  eyebrow: string;
  title: ReactNode;
  width?: PageWidth;
  titleClassName?: string;
  children?: ReactNode;
}) {
  return (
    <main className="flex w-full flex-1 flex-col bg-paper text-ink">
      <div className={`mx-auto flex w-full ${WIDTH[width]} flex-col gap-space-24 px-space-16 py-space-48 sm:px-space-24`}>
        <div className="flex flex-col gap-space-8 border-l-4 border-accent pl-space-16">
          <p className="font-mono text-font-size-12 uppercase tracking-widest text-accent">{eyebrow}</p>
          <h1 className={`text-font-size-32 font-semibold tracking-tight ${titleClassName ?? ""}`}>{title}</h1>
        </div>
        {children}
      </div>
    </main>
  );
}
