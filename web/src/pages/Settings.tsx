import { useState, type FormEvent } from "react";
import { ApiError } from "@/api/auth";
import { updateMe, type UpdateMeRequest } from "@/api/me";
import { saveSession, useSession, type StoredSession } from "@/auth/session";
import { SignInPrompt } from "@/components/SignInPrompt";

/** Field-keyed validation errors, e.g. `{ username: "username already taken" }`. */
type FieldErrors = Record<string, string>;

/** One labelled input with its inline error, the same markup Register uses per field. */
function Field(props: {
  name: string;
  label: string;
  type?: string;
  autoComplete?: string;
  value: string;
  error: string | undefined;
  onChange: (value: string) => void;
}) {
  const id = `settings-${props.name}`;
  const errorId = `${props.name}-error`;
  return (
    <div className="flex flex-col gap-space-4">
      <label htmlFor={id} className="text-font-size-14">
        {props.label}
      </label>
      <input
        id={id}
        name={props.name}
        type={props.type}
        autoComplete={props.autoComplete}
        value={props.value}
        onChange={(event) => props.onChange(event.target.value)}
        aria-describedby={props.error ? errorId : undefined}
      />
      {props.error ? (
        <p id={errorId} className="text-font-size-14 text-stress-fail">
          {props.error}
        </p>
      ) : null}
    </div>
  );
}

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
    <main className="flex min-h-screen flex-col items-center justify-center gap-space-16 bg-paper px-space-16 text-ink">
      <h1 className="text-font-size-32 font-semibold">Account settings</h1>
      {saved ? (
        <p role="status" className="text-font-size-14 text-stress-ok">
          Settings saved.
        </p>
      ) : null}
      {formError !== null ? (
        <p role="alert" className="text-font-size-14 text-stress-fail">
          {formError}
        </p>
      ) : null}
      <form
        onSubmit={(event) => {
          void handleSubmit(event);
        }}
        className="flex w-full max-w-[24rem] flex-col gap-space-12"
      >
        <Field
          name="username"
          label="Display name"
          value={username}
          error={fieldErrors.username}
          onChange={setUsername}
        />
        <Field
          name="email"
          label="New email (leave blank to keep)"
          type="email"
          value={email}
          error={fieldErrors.email}
          onChange={setEmail}
        />
        <Field
          name="password"
          label="New password (leave blank to keep)"
          type="password"
          autoComplete="new-password"
          value={password}
          error={fieldErrors.password}
          onChange={setPassword}
        />
        <Field
          name="current_password"
          label="Current password (needed to change email or password)"
          type="password"
          autoComplete="current-password"
          value={currentPassword}
          error={fieldErrors.current_password}
          onChange={setCurrentPassword}
        />
        <button type="submit" className="text-font-size-16">
          Save changes
        </button>
      </form>
    </main>
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
