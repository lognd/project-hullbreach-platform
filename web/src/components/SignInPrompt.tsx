import { Page } from "@/components/Page";
import { AppLink } from "@/components/AppLink";

// frob:doc docs/index.md#account-settings-page
/** Shown in place of a signed-in page when there is no session: a heading and a log-in link, so no page requests data it cannot authorize. */
export function SignInPrompt({ title, reason }: { title: string; reason: string }) {
  return (
    <Page eyebrow="Signed out" title={title}>
      <p className="text-font-size-16 text-muted">
        <AppLink href="/login" className="font-medium text-accent underline underline-offset-4 hover:text-ink">
          Log in
        </AppLink>{" "}
        {reason}
      </p>
    </Page>
  );
}
