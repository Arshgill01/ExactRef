import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";

process.env.EXACTREF_STORE_PATH = path.join(mkdtempSync(path.join(tmpdir(), "exactref-")), "store.json");
import { applyHumanVerification, classifyIdentifier } from "@/lib/provenance";
import { diffIdentifiers, firstMismatchIndex, identifiersEqual } from "@/lib/diff";
import { compileIdentifierTask } from "@/lib/task";
import { interpretWait } from "@/lib/wait";
import { listCases, replayCase, verifyCase, viewCase } from "@/lib/cases";
import { maskIdentifier } from "@/lib/mask";
import { runExactRefCli } from "@/lib/exactref-cli";

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
      intended: "07198FECTIST",
    });
    expect(compiled.leaksIntended).toBe(false);
    expect(compiled.task).not.toMatch(/07198FECTIST/);
    expect(compiled.task).toMatch(/Do not interrupt/);
  });

  it("flags a fact that repeats the intended identifier", () => {
    const compiled = compileIdentifierTask({
      purpose: "Obtain the off-hire reference.",
      fieldLabel: "off-hire reference",
      destinationLabel: "the test desk",
      factsTheAgentMayState: ["The reference is 07198FECTIST."],
      intended: "07198FECTIST",
    });
    expect(compiled.leaksIntended).toBe(true);
  });
});

describe("identifiersEqual", () => {
  it("ignores hyphens, spaces, and case", () => {
    expect(identifiersEqual("TK-44019", "tk 44019")).toBe(true);
    expect(identifiersEqual("PO-1040", "PO-1O40")).toBe(false);
  });
});

describe("applyHumanVerification", () => {
  const observation = {
    field: "ticket",
    intended: "TK-44019",
    extracted: "TK-44019",
    readbackConfirmed: true,
    evidenceKind: "verbatim_span" as const,
    evidenceText: "TK-44019",
    secondChannelMatch: false,
  };

  it("stays unverified without a second-channel claim", () => {
    const decision = applyHumanVerification({
      observation,
      typed: "TK-44019",
      claimsSecondChannel: false,
    });
    expect(decision.writable).toBe(false);
    expect(decision.provenance).toBe("conversational_confirmed");
  });

  it("accepts a hyphenless typed match when the operator claims a second channel", () => {
    const decision = applyHumanVerification({
      observation,
      typed: "tk44019",
      claimsSecondChannel: true,
    });
    expect(decision.writable).toBe(true);
    expect(decision.provenance).toBe("independently_verified");
  });
});

describe("maskIdentifier", () => {
  it("keeps the last four characters", () => {
    expect(maskIdentifier("07198FECTIST")).toBe("••••••••TIST");
    expect(maskIdentifier("AB12")).toBe("AB12");
  });
});

describe("exactref CLI", () => {
  it("classifies the live F/S miss as a blocked write", () => {
    const result = runExactRefCli([
      "classify",
      "--intended",
      "07198FECTIST",
      "--extracted",
      "07198SECTIST",
      "--readback",
    ]);
    expect(result.code).toBe(2);
    expect(JSON.parse(result.stdout).provenance).toBe("mismatch");
  });

  it("exits 0 only after typed second-channel verification", () => {
    const refused = runExactRefCli([
      "verify",
      "--intended",
      "07198FECTIST",
      "--extracted",
      "07198SECTIST",
      "--typed",
      "07198SECTIST",
      "--second-channel",
    ]);
    expect(refused.code).toBe(2);
    const accepted = runExactRefCli([
      "verify",
      "--intended",
      "07198FECTIST",
      "--extracted",
      "07198SECTIST",
      "--typed",
      "07198FECTIST",
      "--second-channel",
    ]);
    expect(accepted.code).toBe(0);
    expect(JSON.parse(accepted.stdout).writable).toBe(true);
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
  it("lists the fixture cases and FS-01 is not writable", () => {
    const cases = listCases();
    expect(cases.map((item) => item.id)).toEqual(["FS-01", "FS-02", "FS-03", "FS-04", "FS-05"]);
    expect(viewCase("FS-01")?.decision.writable).toBe(false);
    expect(viewCase("FS-01")?.decision.provenance).toBe("mismatch");
    expect(viewCase("FS-05")?.decision.provenance).toBe("mismatch");
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
