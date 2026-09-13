import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";

process.env.EXACTREF_STORE_PATH = path.join(mkdtempSync(path.join(tmpdir(), "exactref-")), "store.json");
import { applyHumanVerification, classifyIdentifier } from "@/lib/provenance";
import { diffIdentifiers, firstMismatchIndex } from "@/lib/diff";
import { compileIdentifierTask } from "@/lib/task";
import { interpretWait } from "@/lib/wait";
import { listCases, replayCase, verifyCase, viewCase } from "@/lib/cases";

describe("classifyIdentifier", () => {
  it("marks the live F/S case as mismatch even after readback yes", () => {
    const decision = classifyIdentifier({
      field: "off_hire_reference",
      intended: "07198FECTIST",
      extracted: "07198SECTIST",
      readbackConfirmed: true,
      evidenceKind: "synthesized_support",
      evidenceText: "yes",
      secondChannelMatch: false,
    });
    expect(decision.provenance).toBe("mismatch");
    expect(decision.writable).toBe(false);
  });

  it("does not treat readback confirmation as independent verification", () => {
    const decision = classifyIdentifier({
      field: "ticket",
      intended: "TK-44019",
      extracted: "TK-44019",
      readbackConfirmed: true,
      evidenceKind: "verbatim_span",
      evidenceText: "TK-44019",
      secondChannelMatch: false,
    });
    expect(decision.provenance).toBe("conversational_confirmed");
    expect(decision.writable).toBe(false);
  });

  it("allows a write only after a second-channel match", () => {
    const decision = classifyIdentifier({
      field: "ticket",
      intended: "TK-44019",
      extracted: "TK-44019",
      readbackConfirmed: true,
      evidenceKind: "verbatim_span",
      evidenceText: "TK-44019",
      secondChannelMatch: true,
    });
    expect(decision.provenance).toBe("independently_verified");
    expect(decision.writable).toBe(true);
  });

  it("stays unknown when nothing was extracted", () => {
    const decision = classifyIdentifier({
      field: "pickup",
      intended: null,
      extracted: "  ",
      readbackConfirmed: false,
      evidenceKind: "none",
      evidenceText: null,
      secondChannelMatch: false,
    });
    expect(decision.provenance).toBe("unknown");
  });
});

describe("diffIdentifiers", () => {
  it("points at the F/S substitution", () => {
    const cells = diffIdentifiers("07198FECTIST", "07198SECTIST");
    expect(firstMismatchIndex(cells)).toBe(5);
    expect(cells[5]).toEqual({ intended: "F", extracted: "S", mark: "changed" });
  });
});

describe("compileIdentifierTask", () => {
  it("does not leak the intended identifier into the outbound task", () => {
    const compiled = compileIdentifierTask({
      purpose: "Obtain the off-hire reference.",
      fieldLabel: "off-hire reference",
      destinationLabel: "the test desk",
      factsTheAgentMayState: ["Ask only for the reference they recorded."],
    });
    expect(compiled.leaksIntended).toBe(false);
    expect(compiled.task).not.toMatch(/07198FECTIST/);
    expect(compiled.task).toMatch(/Do not interrupt/);
  });
});

describe("interpretWait", () => {
  it("does not treat queued-plus-activity as idle", () => {
    const decision = interpretWait({
      surface: "calls",
      topLevelStatus: "queued",
      hasAttemptActivity: true,
      structuredResult: null,
      goalResult: null,
      goalError: null,
      localWaitTimedOut: false,
    });
    expect(decision.treatAsIdle).toBe(false);
    expect(decision.note).toMatch(/queued/i);
  });

  it("does not treat a local timeout as hangup", () => {
    const decision = interpretWait({
      surface: "calls",
      topLevelStatus: "queued",
      hasAttemptActivity: true,
      structuredResult: null,
      goalResult: null,
      goalError: null,
      localWaitTimedOut: true,
    });
    expect(decision.treatTimeoutAsHangup).toBe(false);
  });
});

describe("cases", () => {
  it("lists four fixture cases and FS-01 is not writable", () => {
    const cases = listCases();
    expect(cases.map((item) => item.id)).toEqual(["FS-01", "FS-02", "FS-03", "FS-04"]);
    expect(viewCase("FS-01")?.decision.writable).toBe(false);
    expect(viewCase("FS-01")?.decision.provenance).toBe("mismatch");
  });

  it("requires typing the intended value plus a second-channel claim", () => {
    replayCase("FS-01");
    const refused = verifyCase("FS-01", "07198SECTIST", true);
    expect(refused?.decision.writable).toBe(false);
    const accepted = verifyCase("FS-01", "07198FECTIST", true);
    expect(accepted?.decision.writable).toBe(true);
    expect(accepted?.decision.provenance).toBe("independently_verified");
  });
});
