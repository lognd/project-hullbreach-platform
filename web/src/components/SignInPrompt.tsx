// frob:doc docs/index.md#account-settings-page
/** Shown in place of a signed-in page when there is no session: a heading and a log-in link, so no page requests data it cannot authorize. */
export function SignInPrompt({ title, reason }: { title: string; reason: string }) {
  return (
    <main className="flex flex-col items-center gap-space-8 bg-paper px-space-16 py-space-48 text-ink">
      <h1 className="text-font-size-32 font-semibold">{title}</h1>
      <p className="text-font-size-16 text-muted">
        <a href="/login" className="text-accent">
          Log in
        </a>{" "}
        {reason}
      </p>
    </main>
  );
}
