import type { AnchorHTMLAttributes, MouseEvent } from "react";
import { navigate } from "@/components/navigate";

/** True for a click the browser should handle itself: another button, or a modifier asking for a new tab/window. */
function isBrowserClick(event: MouseEvent<HTMLAnchorElement>): boolean {
  return (
    event.button !== 0 ||
    event.metaKey ||
    event.ctrlKey ||
    event.shiftKey ||
    event.altKey
  );
}

// frob:doc docs/index.md#routing-and-page-shell
/** A real `<a href>` that navigates in-app on a plain click, so following it keeps the session; usable with or without a router (Header renders in isolation tests). */
export function AppLink({
  href,
  onClick,
  ...rest
}: AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) {
  return (
    <a
      href={href}
      onClick={(event) => {
        onClick?.(event);
        if (event.defaultPrevented || isBrowserClick(event)) {
          return;
        }
        event.preventDefault();
        navigate(href);
      }}
      {...rest}
    />
  );
}
