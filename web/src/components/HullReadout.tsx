/** The ship, bow to the right, one character per hull block: o holding, w stressed, x breaching, . empty space. */
const HULL = [
  "...oooo.....",
  ".ooooooooo..",
  "ooooooowwwo.",
  "oooooowwxxoo",
  "ooooooowwwo.",
  ".ooooooooo..",
  "...oooo.....",
];

/** Fill per block state, the same green-amber-red the game draws for hull stress. */
const FILL: Record<string, string> = {
  o: "bg-stress-ok",
  w: "bg-stress-warn",
  x: "bg-stress-fail",
};

/** Legend rows: block state key and the word the game uses for it. */
const LEGEND = [
  ["o", "Holding"],
  ["w", "Stressed"],
  ["x", "Breaching"],
] as const;

// frob:doc docs/index.md#visual-design-rules
/** The landing page's illustration: a block-built hull drawn as a stress map with a breach forming at the bow, so the first screen shows the game, not a stock hero. */
export function HullReadout() {
  return (
    <figure
      role="img"
      aria-label="A ship built from blocks, colored by hull stress, with a breach forming at the bow."
      className="flex flex-col gap-space-16 border border-line bg-panel p-space-16 sm:p-space-24"
    >
      <p className="font-mono text-font-size-12 uppercase tracking-widest text-muted">
        Hull stress / bow section
      </p>
      <div className="grid w-fit grid-cols-12 gap-space-4">
        {HULL.flatMap((row, y) =>
          [...row].map((cell, x) => (
            <span
              key={`${x}-${y}`}
              className={`block h-space-16 w-space-16 rounded-radius-2 sm:h-space-24 sm:w-space-24 lg:h-space-32 lg:w-space-32 ${FILL[cell] ?? ""}`}
            />
          )),
        )}
      </div>
      <ul className="flex flex-wrap gap-x-space-16 gap-y-space-8 font-mono text-font-size-12 uppercase tracking-wider text-muted">
        {LEGEND.map(([key, label]) => (
          <li key={key} className="flex items-center gap-space-8">
            <span className={`block h-space-12 w-space-12 rounded-radius-2 ${FILL[key]}`} />
            {label}
          </li>
        ))}
      </ul>
    </figure>
  );
}
