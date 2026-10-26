import { useState, type FormEvent } from "react";
import { ApiError } from "@/api/auth";
import { updateMe, type UpdateMeRequest } from "@/api/me";
import { saveSession, useSession, type StoredSession } from "@/auth/session";
import { Button } from "@/components/Button";
import { Notice } from "@/components/Notice";
import { Page } from "@/components/Page";
import { Panel } from "@/components/Readout";
import { SignInPrompt } from "@/components/SignInPrompt";
import { TextField } from "@/components/TextField";

/** Id of the form-level error banner, referenced by the form's aria-describedby. */
const FORM_ERROR_ID = "settings-form-error";

/** Field-keyed validation errors, e.g. `{ username: "username already taken" }`. */
type FieldErrors = Record<string, string>;

/** The form for a known session: sends only changed fields, and shows server errors next to the offending field or as a banner. */
function SettingsForm({ session }: { session: StoredSession }) {
  const [username, setUsername] = useState(session.username);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setFieldErrors({});
    setFormError(null);
    setSaved(false);

    const payload: UpdateMeRequest = {};
    if (username.trim() !== session.username) {
      payload.username = username.trim();
    }
    if (email !== "") {
      payload.email = email.trim();
    }
    if (password !== "") {
      payload.password = password;
    }
    if (Object.keys(payload).length === 0) {
      setFormError("Nothing to change.");
      return;
    }
    if (payload.email !== undefined || payload.password !== undefined) {
      if (currentPassword === "") {
        setFieldErrors({
          current_password: "Enter your current password to change your email or password.",
        });
        return;
      }
      payload.current_password = currentPassword;
    }

    try {
      const profile = await updateMe(session.token, payload);
      saveSession({ ...session, username: profile.username });
      setUsername(profile.username);
      setEmail("");
      setPassword("");
      setCurrentPassword("");
      setSaved(true);
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

  return (
    <Page eyebrow="Account" title="Account settings" width="form">
      {saved ? (
        <Notice tone="ok" role="status">
          Settings saved.
        </Notice>
      ) : null}
      {formError !== null ? (
        <Notice tone="error" role="alert" id={FORM_ERROR_ID}>
          {formError}
        </Notice>
      ) : null}
      <Panel className="p-space-24">
      <form
        onSubmit={(event) => {
          void handleSubmit(event);
        }}
        aria-describedby={formError !== null ? FORM_ERROR_ID : undefined}
        className="flex flex-col gap-space-16"
      >
        <fieldset className="m-space-0 flex min-w-0 flex-col gap-space-16 border-0 p-space-0">
          <legend className="float-left w-full pb-space-4 font-mono text-font-size-12 font-semibold uppercase tracking-widest text-accent">Identity</legend>
        <TextField
          id="settings-username"
          name="username"
          label="Display name"
          autoComplete="username"
          value={username}
          error={fieldErrors.username}
          onChange={setUsername}
        />
        </fieldset>
        <fieldset className="m-space-0 flex min-w-0 flex-col gap-space-16 border-0 p-space-0 border-t border-line pt-space-16">
          <legend className="float-left w-full pb-space-4 font-mono text-font-size-12 font-semibold uppercase tracking-widest text-accent">Credentials</legend>
        <TextField
          id="settings-email"
          name="email"
          label="New email"
          type="email"
          autoComplete="email"
          hint="Blank keeps the current address."
          value={email}
          error={fieldErrors.email}
          onChange={setEmail}
        />
        <TextField
          id="settings-password"
          name="password"
          label="New password"
          type="password"
          autoComplete="new-password"
          hint="Blank keeps the current password."
          value={password}
          error={fieldErrors.password}
          onChange={setPassword}
        />
        <TextField
          id="settings-current_password"
          name="current_password"
          label="Current password"
          type="password"
          autoComplete="current-password"
          hint="Required to change email or password."
          value={currentPassword}
          error={fieldErrors.current_password}
          onChange={setCurrentPassword}
        />
        </fieldset>
        <Button type="submit" variant="primary">
          Save changes
        </Button>
      </form>
      </Panel>
    </Page>
  );
}

// frob:doc docs/index.md#account-settings-page
/** Account settings page: edit display name, email and password via PATCH /api/v1/me; signed out it asks the visitor to log in instead. */
export function Settings() {
  const session = useSession();
  if (session === null) {
    return <SignInPrompt title="Account settings" reason="to change your account." />;
  }
  return <SettingsForm session={session} />;
}
