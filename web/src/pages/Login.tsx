import { useState, type FormEvent } from "react";
import { ApiError, login } from "@/api/auth";
import { saveSession } from "@/auth/session";
import { AppLink } from "@/components/AppLink";
import { Button } from "@/components/Button";
import { navigate } from "@/components/navigate";
import { Notice } from "@/components/Notice";
import { Page } from "@/components/Page";
import { TextField } from "@/components/TextField";

/** Id of the form-level error banner, referenced by the form's aria-describedby. */
const FORM_ERROR_ID = "login-form-error";

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** Login form: submits to POST /api/v1/auth/login, keeps the session in memory, and moves home in-app (a page load would drop it); shows a form-level banner on 401/429. */
export function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setFormError(null);
    try {
      const response = await login({ username, password });
      saveSession({
        token: response.token,
        userId: response.user.id,
        username: response.user.username,
        role: response.user.role,
      });
      navigate("/");
    } catch (error) {
      if (error instanceof ApiError) {
        setFormError(error.detail);
      } else {
        setFormError("Something went wrong. Please try again.");
      }
    }
  }

  return (
    <Page eyebrow="Pilot access" title="Log in" width="form">
      {formError !== null ? (
        <Notice tone="error" role="alert" id={FORM_ERROR_ID}>
          {formError}
        </Notice>
      ) : null}
      <form
        onSubmit={(event) => {
          void handleSubmit(event);
        }}
        aria-describedby={formError !== null ? FORM_ERROR_ID : undefined}
        className="flex flex-col gap-space-16"
      >
        <TextField
          id="login-username"
          name="username"
          label="Username"
          autoComplete="username"
          value={username}
          error={undefined}
          onChange={setUsername}
        />
        <TextField
          id="login-password"
          name="password"
          label="Password"
          type="password"
          autoComplete="current-password"
          value={password}
          error={undefined}
          onChange={setPassword}
        />
        <Button type="submit" variant="primary">
          Log in
        </Button>
      </form>
      <p className="text-font-size-14 text-muted">
        No account?{" "}
        <AppLink href="/register" className="font-medium text-accent underline underline-offset-4 hover:text-ink">
          Register
        </AppLink>
      </p>
    </Page>
  );
}
