// Visual design rules crunk has no lint for (see crunk.toml [lint] and
// docs/index.md#visual-design-rules): no gradients, shadows, blur or glass,
// and ASCII-only source. crunk already rejects off-palette colors,
// off-scale spacing/radii and alpha-tinted utilities; this closes the rest.
import { readdirSync, readFileSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { describe, expect, it } from "vitest";

// Vitest runs from the repo root (vite.config.ts sits there, root "web").
const SRC = resolve(process.cwd(), "web/src");

/** Every file under `dir`, recursively. */
function walk(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) =>
    entry.isDirectory() ? walk(join(dir, entry.name)) : [join(dir, entry.name)],
  );
}

/** Tailwind utilities that draw gradients, shadows, blur or see-through glass. */
const BANNED_UTILITY =
  /(?<=^|[\s"'`:{])(?:shadow(?:-[\w/[\]#.-]+)?|drop-shadow(?:-[\w/[\]#.-]+)?|blur(?:-[\w[\].-]+)?|backdrop-[\w[\]().-]+|bg-gradient-[\w-]+|bg-(?:linear|radial|conic)(?:-[\w[\]().,%-]+)?|bg-clip-text|text-transparent|(?:from|via|to)-[a-z][\w[\]#%.-]*)(?=$|[\s"'`}])/gm;

/** CSS declarations for the same effects, for hand-written stylesheets. */
const BANNED_CSS = /(?:linear|radial|conic)-gradient\(|box-shadow\s*:|text-shadow\s*:|backdrop-filter\s*:|filter\s*:\s*blur/g;

/** `file:line: match` for every hit of `pattern` in `files`, so a failure names the offender. */
function hits(files: string[], pattern: RegExp): string[] {
  return files.flatMap((file) =>
    readFileSync(file, "utf8")
      .split("\n")
      .flatMap((line, index) =>
        [...line.matchAll(pattern)].map(
          (match) => `${relative(SRC, file)}:${index + 1}: ${match[0]}`,
        ),
      ),
  );
}

const files = walk(SRC);
const tsx = files.filter((file) => file.endsWith(".tsx"));
const css = files.filter((file) => file.endsWith(".css"));

describe("visual design rules", () => {
  it("finds the sources it is meant to scan", () => {
    expect(tsx.length).toBeGreaterThan(0);
    expect(css.length).toBeGreaterThan(0);
  });

  it("uses no gradient, shadow, blur or glass utilities in className strings", () => {
    expect(hits(tsx, BANNED_UTILITY)).toEqual([]);
  });

  it("declares no gradient, shadow, blur or backdrop filter in CSS", () => {
    expect(hits(css, BANNED_CSS)).toEqual([]);
  });

  it("keeps every source file ASCII (no emoji, no decorative unicode)", () => {
    expect(hits(files, /[^\t\r -~]/g)).toEqual([]);
  });

  it("the utility ban catches what it claims to", () => {
    const sample = [
      'className="shadow-lg"',
      'className="p-space-8 drop-shadow-xl"',
      'className="backdrop-blur-md bg-panel"',
      'className="bg-gradient-to-r from-accent to-ink"',
      'className="bg-linear-to-r via-accent"',
      'className="bg-clip-text text-transparent"',
      'className="hover:blur-sm"',
    ].join("\n");
    const found = [...sample.matchAll(BANNED_UTILITY)].map((match) => match[0]);
    expect(found).toEqual([
      "shadow-lg",
      "drop-shadow-xl",
      "backdrop-blur-md",
      "bg-gradient-to-r",
      "from-accent",
      "to-ink",
      "bg-linear-to-r",
      "via-accent",
      "bg-clip-text",
      "text-transparent",
      "blur-sm",
    ]);
    expect("Back to the hangar; up-to-date; border-accent".match(BANNED_UTILITY)).toBeNull();
  });
});
