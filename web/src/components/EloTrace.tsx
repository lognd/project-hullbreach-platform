import { useId } from "react";

/** Drawing space of the trace in SVG user units; the SVG scales to its panel via viewBox. */
const WIDTH = 360;
const HEIGHT = 140;
/** Inset on every side so lines and square markers never touch or cross the frame. */
const PAD = 14;
/** Marker edge length in user units. */
const MARK = 6;

/** One plotted rating: its position inside the frame and the rating it stands for. */
export type TracePoint = { x: number; y: number; rating: number };

// frob:doc docs/index.md#visual-design-rules
/** Maps ratings (oldest first) to points evenly spaced in x and scaled in y, always inset by PAD so nothing leaves the frame; a flat series sits on the middle line. */
export function traceGeometry(ratings: readonly number[]): TracePoint[] {
  const low = Math.min(...ratings);
  const high = Math.max(...ratings);
  const span = high - low;
  const innerW = WIDTH - 2 * PAD;
  const innerH = HEIGHT - 2 * PAD;
  return ratings.map((rating, index) => ({
    x:
      PAD +
      (ratings.length === 1 ? innerW / 2 : (index / (ratings.length - 1)) * innerW),
    y: span === 0 ? HEIGHT / 2 : PAD + (1 - (rating - low) / span) * innerH,
    rating,
  }));
}

/** Evenly spaced guide lines inside the inset frame, as SVG path data. */
const GRID_PATH = [0, 1, 2, 3]
  .map((row) => `M${PAD} ${PAD + (row / 3) * (HEIGHT - 2 * PAD)}H${WIDTH - PAD}`)
  .concat(
    [0, 1, 2, 3, 4].map(
      (col) => `M${PAD + (col / 4) * (WIDTH - 2 * PAD)} ${PAD}V${HEIGHT - PAD}`,
    ),
  )
  .join("");

// frob:doc docs/index.md#visual-design-rules
/** ELO over time as a square-marker line chart in a bordered, clipped frame (the newest point in signal orange); fewer than two ratings shows a hatched "no data yet" placeholder with an opaque label chip. */
export function EloTrace({ ratings }: { ratings: readonly number[] }) {
  const hatchId = useId();
  const enough = ratings.length >= 2;
  const points = enough ? traceGeometry(ratings) : [];
  const last = points.at(-1);
  return (
    <figure className="m-space-0 flex flex-col gap-space-8">
      <div className="relative overflow-hidden border border-line bg-paper">
        <svg
          viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
          role="img"
          aria-label={
            enough
              ? `ELO trace over the last ${ratings.length - 1} matches, from ${ratings[0]} to ${ratings[ratings.length - 1]}.`
              : "ELO trace placeholder: not enough matches to draw a line yet."
          }
          className="block h-auto w-full overflow-hidden"
          fill="none"
        >
          {enough ? (
            <>
              <path
                d={GRID_PATH}
                stroke="var(--color-line)"
                strokeWidth="1"
                vectorEffect="non-scaling-stroke"
              />
              <polyline
                points={points.map((p) => `${p.x},${p.y}`).join(" ")}
                stroke="var(--color-accent)"
                strokeWidth="2"
                strokeLinejoin="miter"
                vectorEffect="non-scaling-stroke"
              />
              {points.slice(0, -1).map((p) => (
                <rect
                  key={p.x}
                  x={p.x - MARK / 2}
                  y={p.y - MARK / 2}
                  width={MARK}
                  height={MARK}
                  fill="var(--color-paper)"
                  stroke="var(--color-accent)"
                  strokeWidth="1.5"
                  vectorEffect="non-scaling-stroke"
                />
              ))}
              {last !== undefined ? (
                <rect
                  x={last.x - MARK / 2}
                  y={last.y - MARK / 2}
                  width={MARK}
                  height={MARK}
                  fill="var(--color-signal)"
                  stroke="var(--color-signal)"
                  vectorEffect="non-scaling-stroke"
                />
              ) : null}
            </>
          ) : (
            <>
              <defs>
                <pattern
                  id={hatchId}
                  width="10"
                  height="10"
                  patternUnits="userSpaceOnUse"
                  patternTransform="rotate(45)"
                >
                  <path
                    d="M0 0V10"
                    stroke="var(--color-line)"
                    strokeWidth="1"
                    vectorEffect="non-scaling-stroke"
                  />
                </pattern>
              </defs>
              <rect
                x="0"
                y="0"
                width={WIDTH}
                height={HEIGHT}
                fill={`url(#${hatchId})`}
              />
            </>
          )}
        </svg>
        {enough ? null : (
          <p className="absolute left-1/2 top-1/2 m-space-0 w-max max-w-[90%] -translate-x-1/2 -translate-y-1/2 border border-line bg-panel px-space-12 py-space-8 text-center font-mono text-font-size-12 uppercase tracking-widest text-muted">
            No data yet - play 2 matches
          </p>
        )}
      </div>
      {enough ? (
        <figcaption className="font-mono text-font-size-12 uppercase tracking-widest text-muted">
          Last {ratings.length - 1} matches: {ratings[0]} to{" "}
          {ratings[ratings.length - 1]}
        </figcaption>
      ) : null}
    </figure>
  );
}
