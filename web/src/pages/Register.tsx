import { useState, type FormEvent } from "react";
import { ApiError, register } from "@/api/auth";
import { Button, ButtonLink } from "@/components/Button";
import { Notice } from "@/components/Notice";
import { Page } from "@/components/Page";
import { TextField } from "@/components/TextField";

/** Field-keyed validation errors, e.g. `{ username: "username already taken" }`. */
type FieldErrors = Record<string, string>;

/** Id of the form-level error banner, referenced by the form's aria-describedby. */
const FORM_ERROR_ID = "register-form-error";

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** Registration form: submits to POST /api/v1/auth/register and shows errors inline next to the offending field, or a form-level banner for a non-field error. */
export function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setFieldErrors({});
    setFormError(null);
    try {
      await register({ username, email, password });
      setSubmitted(true);
    } catch (error) {
      if (error instanceof ApiError && error.field !== undefined) {
        setFieldErrors({ [error.field]: error.detail });
      } else if (error instanceof ApiError) {
        setFormError(error.detail);
      } else {
        setFormError("Something went wrong. Please try again.");
      }
    }
  }

  if (submitted) {
    return (
      <Page eyebrow="Callsign registered" title="Registration complete" width="form">
        <p className="text-font-size-16 text-muted">Your account is ready. Log in to start climbing from 1200.</p>
        <div>
          <ButtonLink href="/login" variant="primary">
            Log in
          </ButtonLink>
        </div>
      </Page>
    );
  }

  return (
    <Page eyebrow="New pilot" title="Register" width="form">
      <p className="text-font-size-16 text-muted">Claim a callsign. Your ELO starts at 1200.</p>
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
          id="register-username"
          name="username"
          label="Username"
          autoComplete="username"
          value={username}
          error={fieldErrors.username}
          onChange={setUsername}
        />
        <TextField
          id="register-email"
          name="email"
          label="Email"
          type="email"
          autoComplete="email"
          value={email}
          error={fieldErrors.email}
          onChange={setEmail}
        />
        <TextField
          id="register-password"
          name="password"
          label="Password"
          type="password"
          autoComplete="new-password"
          value={password}
          error={fieldErrors.password}
          onChange={setPassword}
        />
        <Button type="submit" variant="primary">
          Register
        </Button>
      </form>
    </Page>
  );
}
