#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const result = spawnSync(
  process.execPath,
  [path.join(root, "node_modules/vite-node/vite-node.mjs"), path.join(root, "src/cli.ts"), ...process.argv.slice(2)],
  { stdio: "inherit", cwd: root },
);
process.exit(result.status ?? 1);
