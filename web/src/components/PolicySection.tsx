import type { ReactNode } from "react";
import { SectionHeading } from "@/components/Readout";

// frob:ticket 01M2H5T11HZP2VXR9KV24Q8RV3
// frob:doc docs/index.md#landing-and-policy-pages
/** One titled section of a policy page: an h2 plus prose, so both policy pages read the same way. */
export function PolicySection({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <section aria-labelledby={id} className="flex flex-col gap-space-8">
      <SectionHeading id={id}>{title}</SectionHeading>
      <div className="flex flex-col gap-space-8 text-font-size-16 text-muted">
        {children}
      </div>
    </section>
  );
}
