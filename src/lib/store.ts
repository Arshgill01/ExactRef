import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import type { IdentifierDecision } from "./provenance";

function storeFile() {
  return process.env.EXACTREF_STORE_PATH ?? path.join(process.cwd(), ".data", "dispositions.json");
}

type Store = Record<string, IdentifierDecision>;

function readStore(): Store {
  try {
    return JSON.parse(readFileSync(storeFile(), "utf8")) as Store;
  } catch {
    return {};
  }
}

function writeStore(store: Store) {
  const file = storeFile();
  mkdirSync(path.dirname(file), { recursive: true });
  writeFileSync(file, `${JSON.stringify(store, null, 2)}\n`);
}

export function getDisposition(id: string): IdentifierDecision | undefined {
  return readStore()[id];
}

export function setDisposition(id: string, decision: IdentifierDecision) {
  const store = readStore();
  store[id] = decision;
  writeStore(store);
}

export function clearDisposition(id: string) {
  const store = readStore();
  delete store[id];
  writeStore(store);
}

export function clearAllDispositions() {
  writeStore({});
}
