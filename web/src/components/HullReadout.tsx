// frob:doc docs/index.md#visual-design-rules
/** The landing page's illustration: a side-view spaceship line drawing (hull, cockpit, fins, engine nozzles) with a length dimension, inside a bordered padded panel. */
export function HullReadout() {
  return (
    <figure className="m-space-0 overflow-hidden border border-accent bg-panel p-space-16 sm:p-space-24">
      <svg
        viewBox="0 0 520 250"
        role="img"
        aria-label="Line drawing of a spaceship in side view: pointed nose, cockpit, swept fins and three engine nozzles."
        className="block h-auto w-full overflow-hidden"
        fill="none"
        stroke="var(--color-accent)"
        strokeWidth="1.5"
        strokeLinejoin="miter"
      >
        <path
          d="M24 60H496M24 160H496"
          stroke="var(--color-line)"
          vectorEffect="non-scaling-stroke"
        />
        <path
          d="M60 105L120 85L360 80L470 105L500 120L470 135L360 160L120 155L60 135Z"
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
        />
        <path
          d="M360 80L395 118H470M360 160L395 122"
          stroke="var(--color-line)"
          vectorEffect="non-scaling-stroke"
        />
        <path d="M400 105L440 108L440 132L400 135Z" vectorEffect="non-scaling-stroke" />
        <path
          d="M150 85L110 40L215 40L260 82M150 155L110 200L215 200L260 158"
          vectorEffect="non-scaling-stroke"
        />
        <path
          d="M60 105H34V115H60M60 125H34V135H60"
          vectorEffect="non-scaling-stroke"
        />
        <path
          d="M200 120H340"
          stroke="var(--color-line)"
          strokeDasharray="4 4"
          vectorEffect="non-scaling-stroke"
        />
        <path
          d="M34 110L12 110M34 130L12 130"
          stroke="var(--color-signal)"
          vectorEffect="non-scaling-stroke"
        />
        <path
          d="M60 222H500M60 216V228M500 216V228"
          vectorEffect="non-scaling-stroke"
        />
        <text
          x="280"
          y="244"
          textAnchor="middle"
          fill="var(--color-accent)"
          stroke="none"
          fontFamily="var(--font-family-mono)"
          fontSize="12"
          letterSpacing="2"
        >
          LENGTH 24.0 M
        </text>
      </svg>
    </figure>
  );
}
