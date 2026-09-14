#!/usr/bin/env node
// Thin wrapper: the skill script is the single source of the rules and has no dependencies.
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const result = spawnSync(
  process.execPath,
  [path.join(root, "skills/exact-ref/scripts/exactref.mjs"), ...process.argv.slice(2)],
  { stdio: "inherit", cwd: root },
);
process.exit(result.status ?? 1);
