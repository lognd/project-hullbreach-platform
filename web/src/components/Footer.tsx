import { AppLink } from "@/components/AppLink";

// frob:doc docs/index.md#routing-and-page-shell
/** Site footer with links to the cookie notice and data policy pages. */
export function Footer() {
  return (
    <footer className="flex flex-wrap items-center gap-x-space-16 gap-y-space-8 border-t border-line bg-paper px-space-16 py-space-12 text-font-size-12 text-muted sm:px-space-24">
      <span className="w-full font-mono uppercase tracking-widest sm:mr-auto sm:w-auto">
        Class project // pre-release
      </span>
      {/* frob:todo 01M2H5T11HZP2VXR9KV24Q8RV3 both links 404 until the data-policy route and page exist */}
      <AppLink
        href="/cookie-policy"
        className="py-space-8 underline underline-offset-4 hover:text-ink"
      >
        Cookie policy
      </AppLink>
      <AppLink
        href="/data-policy"
        className="py-space-8 underline underline-offset-4 hover:text-ink"
      >
        Data policy
      </AppLink>
    </footer>
  );
}
