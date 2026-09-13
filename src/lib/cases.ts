import type { IdentifierDecision, IdentifierObservation } from "./provenance";
import { applyHumanVerification, classifyIdentifier } from "./provenance";
import { compileIdentifierTask } from "./task";
import { interpretWait, type WaitHonesty } from "./wait";
import { clearDisposition, getDisposition, setDisposition } from "./store";

export type CaseRecord = {
  id: string;
  title: string;
  purpose: string;
  fieldLabel: string;
  destinationLabel: string;
  factsTheAgentMayState: string[];
  observation: IdentifierObservation;
  wait: WaitHonesty;
  summary: string;
  liveEligible: boolean;
};

export type CaseView = CaseRecord & {
  decision: IdentifierDecision;
  waitNote: string;
  task: ReturnType<typeof compileIdentifierTask>;
};

export const CASES: CaseRecord[] = [
  {
    id: "FS-01",
    title: "Readback yes, one letter wrong",
    purpose: "Obtain the supplier off-hire reference for a reviewed exception.",
    fieldLabel: "off-hire reference",
    destinationLabel: "the consented test desk (fixture)",
    factsTheAgentMayState: [
      "This is a confirmation call for an existing return request.",
      "Ask only for the reference they recorded.",
    ],
    observation: {
      field: "off_hire_reference",
      intended: "07198FECTIST",
      extracted: "07198SECTIST",
      readbackConfirmed: true,
      evidenceKind: "synthesized_support",
      evidenceText: "zero seven one nine eight F as in Frank… yes",
      secondChannelMatch: false,
    },
    wait: {
      surface: "calls",
      topLevelStatus: "queued",
      hasAttemptActivity: true,
      structuredResult: { identifier: "07198SECTIST" },
      goalResult: null,
      goalError: null,
      localWaitTimedOut: false,
    },
    summary: "Sunday 5 PM — do not schedule from this.",
    liveEligible: false,
  },
  {
    id: "FS-02",
    title: "Contradictory time, summary picked one",
    purpose: "Ask when they can collect. Do not invent a clock time.",
    fieldLabel: "collection window",
    destinationLabel: "the consented test desk (fixture)",
    factsTheAgentMayState: ["The item is waiting for collection."],
    observation: {
      field: "collection_window",
      intended: null,
      extracted: "Sunday 5:00 PM",
      readbackConfirmed: false,
      evidenceKind: "synthesized_support",
      evidenceText: "Sunday morning … 5:00 PM",
      secondChannelMatch: false,
    },
    wait: {
      surface: "calls",
      topLevelStatus: "completed",
      hasAttemptActivity: true,
      structuredResult: { unresolved_time: "Sunday morning / 5:00 PM" },
      goalResult: null,
      goalError: null,
      localWaitTimedOut: false,
    },
    summary: "Sunday 5 PM",
    liveEligible: false,
  },
  {
    id: "FS-03",
    title: "Clean spoken value, no second channel",
    purpose: "Obtain a ticket number.",
    fieldLabel: "ticket number",
    destinationLabel: "the consented test desk (fixture)",
    factsTheAgentMayState: ["Ask for the ticket they just created."],
    observation: {
      field: "ticket_number",
      intended: "TK-44019",
      extracted: "TK-44019",
      readbackConfirmed: true,
      evidenceKind: "verbatim_span",
      evidenceText: "That's TK-44019.",
      secondChannelMatch: false,
    },
    wait: {
      surface: "calls",
      topLevelStatus: "completed",
      hasAttemptActivity: true,
      structuredResult: { identifier: "TK-44019" },
      goalResult: null,
      goalError: null,
      localWaitTimedOut: false,
    },
    summary: "They confirmed the ticket.",
    liveEligible: false,
  },
  {
    id: "FS-04",
    title: "No identifier extracted",
    purpose: "Obtain a pickup number.",
    fieldLabel: "pickup number",
    destinationLabel: "the consented test desk (fixture)",
    factsTheAgentMayState: ["Ask whether a pickup number exists."],
    observation: {
      field: "pickup_number",
      intended: null,
      extracted: null,
      readbackConfirmed: false,
      evidenceKind: "none",
      evidenceText: null,
      secondChannelMatch: false,
    },
    wait: {
      surface: "calls",
      topLevelStatus: "completed",
      hasAttemptActivity: true,
      structuredResult: null,
      goalResult: null,
      goalError: null,
      localWaitTimedOut: false,
    },
    summary: "They said they would call back.",
    liveEligible: false,
  },
];

export function viewCase(id: string): CaseView | null {
  const record = CASES.find((item) => item.id === id);
  if (!record) return null;
  const decision = getDisposition(id) ?? classifyIdentifier(record.observation);
  const wait = interpretWait(record.wait);
  return {
    ...record,
    decision,
    waitNote: wait.note,
    task: compileIdentifierTask(record),
  };
}

export function listCases(): CaseView[] {
  return CASES.map((record) => viewCase(record.id)!);
}

export function replayCase(id: string): CaseView | null {
  clearDisposition(id);
  return viewCase(id);
}

export function verifyCase(
  id: string,
  typed: string,
  claimsSecondChannel: boolean,
): CaseView | null {
  const record = CASES.find((item) => item.id === id);
  if (!record) return null;
  const decision = applyHumanVerification({
    observation: record.observation,
    typed,
    claimsSecondChannel,
  });
  setDisposition(id, decision);
  return viewCase(id);
}

export function keepSpokenOnly(id: string): CaseView | null {
  const record = CASES.find((item) => item.id === id);
  if (!record) return null;
  const decision = classifyIdentifier({
    ...record.observation,
    secondChannelMatch: false,
  });
  setDisposition(id, {
    ...decision,
    writable: false,
    reason: "Operator kept the value as spoken-only. It must not be written as a fact.",
  });
  return viewCase(id);
}
