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
  const errorId = `${props.name}-error`;
  const hintId = `${props.id}-hint`;
  const describedBy = props.error ? errorId : props.hint ? hintId : undefined;
  return (
    <div className="flex flex-col gap-space-4">
      <label htmlFor={props.id} className="font-mono text-font-size-12 uppercase tracking-wider text-muted">
        {props.label}
      </label>
      <input
        id={props.id}
        name={props.name}
        type={props.type}
        autoComplete={props.autoComplete}
        value={props.value}
        onChange={(event) => props.onChange(event.target.value)}
        aria-describedby={describedBy}
        aria-invalid={props.error ? true : undefined}
        className="w-full rounded-radius-2 border border-muted bg-panel px-space-12 py-space-8 text-font-size-16 text-ink hover:border-ink aria-invalid:border-stress-fail"
      />
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
