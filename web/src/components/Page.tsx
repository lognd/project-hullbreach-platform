import type { ReactNode } from "react";
import { AppLink } from "@/components/AppLink";

/** Content column width: narrow for forms, wide for the landing page and lists. */
export type PageWidth = "form" | "content" | "wide";

/** max-width per PageWidth; every page is left-aligned inside it, never centered text. */
const WIDTH: Record<PageWidth, string> = {
  form: "max-w-[28rem]",
  content: "max-w-[48rem]",
  wide: "max-w-[72rem]",
};

/** One step of the "you are here" trail; the last step has no href and is the current page. */
export type Crumb = { label: string; href?: string };

// frob:doc docs/index.md#visual-design-rules
/** The "you are here" trail above a page title: Home plus `crumbs`, the last of which is marked aria-current. */
export function Breadcrumb({ crumbs }: { crumbs: readonly Crumb[] }) {
  const trail: readonly Crumb[] = [{ label: "Home", href: "/" }, ...crumbs];
  return (
    <nav aria-label="Breadcrumb">
      <div className="flex flex-wrap items-center gap-x-space-8 font-mono text-font-size-12 uppercase tracking-widest text-muted">
        {trail.map((crumb, index) => (
          <span key={crumb.label} className="flex items-center gap-space-8">
            {index > 0 ? <span aria-hidden="true">/</span> : null}
            {crumb.href !== undefined ? (
              <AppLink
                href={crumb.href}
                className="py-space-4 underline underline-offset-4 hover:text-ink"
              >
                {crumb.label}
              </AppLink>
            ) : (
              <span aria-current="page" className="text-ink">
                {crumb.label}
              </span>
            )}
          </span>
        ))}
      </div>
    </nav>
  );
}

// frob:doc docs/index.md#visual-design-rules
/** The `<main>` every route renders: breadcrumb, a display-face h1 and a one-line purpose, so every page answers "where am I and what is this for". */
export function Page({
  crumbs,
  title,
  purpose,
  width = "content",
  titleClassName,
  children,
}: {
  crumbs: readonly Crumb[];
  title: ReactNode;
  purpose?: string;
  width?: PageWidth;
  titleClassName?: string;
  children?: ReactNode;
}) {
  return (
    <main className="flex w-full flex-1 flex-col text-ink">
      <div
        className={`mx-auto flex w-full ${WIDTH[width]} flex-col gap-space-24 px-space-16 py-space-32 sm:px-space-24 sm:py-space-48`}
      >
        <div className="flex flex-col gap-space-12">
          <Breadcrumb crumbs={crumbs} />
          <h1
            className={`font-display text-font-size-24 font-normal uppercase tracking-wider sm:text-font-size-32 ${titleClassName ?? ""}`}
          >
            {title}
          </h1>
          {purpose !== undefined ? (
            <p className="max-w-[40rem] text-font-size-16 text-muted">{purpose}</p>
          ) : null}
        </div>
        {children}
      </div>
    </main>
  );
}
