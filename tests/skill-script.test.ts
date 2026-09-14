import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { classifyIdentifier } from "@/lib/provenance";

const SCRIPT = path.join(process.cwd(), "skills/exact-ref/scripts/exactref.mjs");
const FIXTURES = path.join(process.cwd(), "skills/exact-ref/references/fixtures.json");

function run(args: string[]) {
  const result = spawnSync(process.execPath, [SCRIPT, ...args], { encoding: "utf8" });
  return { code: result.status, stdout: result.stdout, stderr: result.stderr };
}

describe("standalone skill script", () => {
  it("agrees with the board rules on every fixture", () => {
    const fixtures = JSON.parse(readFileSync(FIXTURES, "utf8")) as Array<{
      id: string;
      observation: Parameters<typeof classifyIdentifier>[0];
      expect: { provenance: string; writable: boolean };
    }>;
    const rows = JSON.parse(run(["fixtures"]).stdout) as Array<{ id: string; provenance: string; writable: boolean }>;
    for (const fixture of fixtures) {
      const board = classifyIdentifier(fixture.observation);
      const script = rows.find((row) => row.id === fixture.id)!;
      expect(script.provenance).toBe(board.provenance);
      expect(script.provenance).toBe(fixture.expect.provenance);
      expect(script.writable).toBe(fixture.expect.writable);
    }
  });

  it("blocks the live F/S miss with exit 2 and names character 6", () => {
    const result = run(["classify", "--intended", "07198FECTIST", "--extracted", "07198SECTIST", "--readback"]);
    expect(result.code).toBe(2);
    const decision = JSON.parse(result.stdout);
    expect(decision.provenance).toBe("mismatch");
    expect(decision.firstMismatch).toEqual({ index: 5, intended: "F", extracted: "S", mark: "changed" });
  });

  it("gates a saved CALL-E call object", () => {
    const blocked = run(["gate", "--call", "skills/exact-ref/references/call-fs01.json", "--intended", "07198FECTIST"]);
    expect(blocked.code).toBe(2);
    expect(JSON.parse(blocked.stdout).decision.provenance).toBe("mismatch");
  });

  it("refuses to classify a non-terminal call", () => {
    const tmp = path.join(process.cwd(), ".data", "queued-fixture.json");
    const { mkdirSync, writeFileSync } = require("node:fs") as typeof import("node:fs");
    mkdirSync(path.dirname(tmp), { recursive: true });
    writeFileSync(tmp, JSON.stringify({ status: "queued", attempts: [{}], structured_result: { identifier: "X" } }));
    const result = run(["gate", "--call", tmp, "--intended", "X"]);
    expect(result.code).toBe(2);
    const out = JSON.parse(result.stdout);
    expect(out.decision.provenance).toBe("unknown");
    expect(out.wait.note).toMatch(/Do not create again/);
  });

  it("exits 0 only after a typed second-channel match", () => {
    expect(run(["verify", "--intended", "07198FECTIST", "--extracted", "07198SECTIST", "--typed", "07198SECTIST", "--second-channel"]).code).toBe(2);
    expect(run(["verify", "--intended", "07198FECTIST", "--extracted", "07198SECTIST", "--typed", "07198FECTIST", "--second-channel"]).code).toBe(0);
  });

  it("rejects a task that leaks the intended identifier", () => {
    const result = run(["compile", "--field", "reference", "--destination", "the desk", "--intended", "07198FECTIST", "--fact", "It is 07198FECTIST"]);
    expect(result.code).toBe(2);
    expect(result.stderr).toMatch(/leaked/);
  });
});
