import type { AnchorHTMLAttributes, ButtonHTMLAttributes } from "react";
import { AppLink } from "@/components/AppLink";

/** Primary is the one action a screen exists for; secondary is everything else. */
export type ButtonVariant = "primary" | "secondary";

/** Shared box for both variants: square-cornered, 40px tall, label in the readout face. */
const BASE =
  "inline-flex items-center justify-center gap-space-8 rounded-radius-2 border px-space-16 py-space-8 font-mono text-font-size-14 font-semibold uppercase tracking-wider disabled:cursor-not-allowed disabled:opacity-50";

/** Per-variant fill: primary is solid accent with paper text, secondary an outlined control. */
const VARIANT: Record<ButtonVariant, string> = {
  primary: "border-accent bg-accent text-paper hover:bg-ink hover:border-ink",
  secondary: "border-muted bg-paper text-ink hover:border-ink",
};

// frob:doc docs/index.md#visual-design-rules
/** The class string for a button-looking control, so a link and a button of the same variant are identical. */
export function buttonClass(variant: ButtonVariant): string {
  return `${BASE} ${VARIANT[variant]}`;
}

// frob:doc docs/index.md#visual-design-rules
/** The site's only button style; defaults to type="button" so nothing submits a form by accident. */
export function Button({
  variant = "secondary",
  type = "button",
  className,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant }) {
  return (
    <button
      type={type}
      className={className ? `${buttonClass(variant)} ${className}` : buttonClass(variant)}
      {...rest}
    />
  );
}

// frob:doc docs/index.md#visual-design-rules
/** An in-app link drawn as a button, for calls to action that move to another page. */
export function ButtonLink({
  variant = "secondary",
  href,
  ...rest
}: AnchorHTMLAttributes<HTMLAnchorElement> & { href: string; variant?: ButtonVariant }) {
  return <AppLink href={href} className={buttonClass(variant)} {...rest} />;
}
