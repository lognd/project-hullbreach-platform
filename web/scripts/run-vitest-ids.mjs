#!/usr/bin/env node
// Runs one or more frob-style test node ids ("<file>::<describe path> >
// <test name>") through vitest's actual CLI shape (`vitest run <file> -t
// <name>`), since frob's [[test.runner]] template substitutes a node id
// verbatim as a single positional argument -- a shape pytest understands
// natively but vitest does not. Exits non-zero if any id fails, matching
// what frob's generic runner protocol expects (T-0097).
import { spawnSync } from "node:child_process";
import { readFileSync, unlinkSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

/** Splits one frob node id into its vitest file path and `-t` name pattern.
 * Only the innermost `it()` title is kept for `-t`: vitest's `-t` matches
 * a test's own title, not its full "describe > test" display path, so
 * passing the whole path after "::" selects zero tests (and vitest
 * exits 0 for "nothing matched", which would read as a false pass). */
function splitNodeId(nodeId) {
  const sep = "::";
  const idx = nodeId.indexOf(sep);
  if (idx === -1) {
    throw new Error(`not a "<file>::<name>" node id: ${nodeId}`);
  }
  const fullName = nodeId.slice(idx + sep.length);
  const innermost = fullName.split(" > ").pop();
  return {
    file: nodeId.slice(0, idx),
    name: innermost,
  };
}

const ids = process.argv.slice(2);
if (ids.length === 0) {
  console.error("run-vitest-ids: no node ids given");
  process.exit(1);
}

let failures = 0;
for (const id of ids) {
  const { file, name } = splitNodeId(id);
  const jsonPath = join(
    tmpdir(),
    `run-vitest-ids-${process.pid}-${Math.random().toString(36).slice(2)}.json`,
  );
  const result = spawnSync(
    "npx",
    [
      "vitest",
      "run",
      file,
      "-t",
      name,
      "--reporter=default",
      "--reporter=json",
      `--outputFile.json=${jsonPath}`,
    ],
    { stdio: "inherit" },
  );

  // vitest exits 0 for "matched nothing under this -t filter", which
  // would read as a false pass; cross-check the JSON reporter's own
  // count so a typo'd node id fails loudly instead.
  let selectedCount = 0;
  try {
    const report = JSON.parse(readFileSync(jsonPath, "utf8"));
    // A -t filter that matches nothing leaves every test "pending"
    // (skipped) with numPassedTests=numFailedTests=0 and exit code 0;
    // numTotalTests alone stays at the file's full count either way,
    // so it cannot tell a real match from a typo'd name.
    selectedCount = (report.numPassedTests ?? 0) + (report.numFailedTests ?? 0);
  } catch {
    selectedCount = 0;
  } finally {
    try {
      unlinkSync(jsonPath);
    } catch {
      // best-effort cleanup only
    }
  }

  if (result.status !== 0 || selectedCount === 0) {
    console.error(
      `run-vitest-ids: ${id} -> ${selectedCount} test(s) selected, exit=${result.status}`,
    );
    failures += 1;
  }
}

process.exit(failures === 0 ? 0 : 1);
