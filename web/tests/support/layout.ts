/** Root font size in px, matching crunk.toml's `root_font_size`. */
const ROOT_FONT_PX = 16;

/** Matches a bare (variant-free) fixed width utility such as `w-[24rem]` or `min-w-[320px]`. */
const FIXED_WIDTH = /^(?:min-)?w-\[(\d*\.?\d+)(rem|px)\]$/;

/** Describes every element under `root` whose classes can force it wider than `viewportPx`: a fixed width above it, or text that refuses to wrap. */
export function overflowRisks(root: HTMLElement, viewportPx: number): string[] {
  const risks: string[] = [];
  for (const element of root.querySelectorAll<HTMLElement>("[class]")) {
    for (const token of element.className.split(/\s+/)) {
      if (token === "whitespace-nowrap") {
        risks.push(`${element.tagName.toLowerCase()}: ${token}`);
        continue;
      }
      const match = FIXED_WIDTH.exec(token);
      if (match === null) {
        continue;
      }
      const px = Number(match[1]) * (match[2] === "rem" ? ROOT_FONT_PX : 1);
      if (px > viewportPx) {
        risks.push(`${element.tagName.toLowerCase()}: ${token} (${px}px)`);
      }
    }
  }
  return risks;
}
