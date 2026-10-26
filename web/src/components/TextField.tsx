import { useState } from "react";

// frob:doc docs/index.md#visual-design-rules
/** One labelled input with an optional hint and inline error, both tied to the input via aria-describedby; the error replaces the hint and sets aria-invalid. */
export function TextField(props: {
  id: string;
  name: string;
  label: string;
  type?: string;
  autoComplete?: string;
  hint?: string;
  value: string;
  error: string | undefined;
  onChange: (value: string) => void;
}) {
  const [revealed, setRevealed] = useState(false);
  const isPassword = props.type === "password";
  const errorId = `${props.name}-error`;
  const hintId = `${props.id}-hint`;
  const describedBy = props.error ? errorId : props.hint ? hintId : undefined;
  return (
    <div className="flex flex-col gap-space-4">
      <label htmlFor={props.id} className="font-mono text-font-size-12 uppercase tracking-wider text-muted">
        {props.label}
      </label>
      <div className="relative">
      <input
        id={props.id}
        name={props.name}
        type={isPassword && revealed ? "text" : props.type}
        autoComplete={props.autoComplete}
        value={props.value}
        onChange={(event) => props.onChange(event.target.value)}
        aria-describedby={describedBy}
        aria-invalid={props.error ? true : undefined}
        className={`w-full rounded-radius-2 border border-muted bg-paper py-space-8 pl-space-12 text-font-size-16 text-ink hover:border-ink aria-invalid:border-stress-fail ${isPassword ? "pr-space-64" : "pr-space-12"}`}
      />
      {isPassword ? (
        <button
          type="button"
          aria-pressed={revealed}
          aria-controls={props.id}
          onClick={() => setRevealed((value) => !value)}
          className="absolute inset-y-0 right-0 px-space-12 font-mono text-font-size-12 uppercase tracking-wider text-muted hover:text-ink"
        >
          {revealed ? "Hide" : "Show"}
        </button>
      ) : null}
      </div>
      {props.error ? (
        <p id={errorId} className="text-font-size-14 text-stress-fail">
          {props.error}
        </p>
      ) : props.hint ? (
        <p id={hintId} className="text-font-size-12 text-muted">
          {props.hint}
        </p>
      ) : null}
    </div>
  );
}
