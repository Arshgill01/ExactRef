import { identifiersEqual } from "./diff";

export const PROVENANCE = [
  "unknown",
  "spoken_only",
  "conversational_confirmed",
  "mismatch",
  "independently_verified",
] as const;

export type Provenance = (typeof PROVENANCE)[number];

export type EvidenceKind = "verbatim_span" | "synthesized_support" | "none";

export type IdentifierObservation = {
  field: string;
  intended: string | null;
  extracted: string | null;
  readbackConfirmed: boolean;
  evidenceKind: EvidenceKind;
  evidenceText: string | null;
  secondChannelMatch: boolean;
};

export type IdentifierDecision = IdentifierObservation & {
  provenance: Provenance;
  writable: boolean;
  reason: string;
};

export function classifyIdentifier(input: IdentifierObservation): IdentifierDecision {
  const extracted = input.extracted?.trim() ? input.extracted : null;
  const intended = input.intended?.trim() ? input.intended : null;

  if (!extracted) {
    return {
      ...input,
      extracted: null,
      provenance: "unknown",
      writable: false,
      reason: "No identifier was extracted. Do not invent one.",
    };
  }

  if (input.secondChannelMatch && intended && identifiersEqual(extracted, intended)) {
    return {
      ...input,
      provenance: "independently_verified",
      writable: true,
      reason: "A second channel matched the intended value. Safe to write that value.",
    };
  }

  if (intended && !identifiersEqual(extracted, intended)) {
    return {
      ...input,
      provenance: "mismatch",
      writable: false,
      reason:
        "Extracted value does not match the intended identifier. Readback-plus-yes does not override this.",
    };
  }

  if (input.readbackConfirmed) {
    return {
      ...input,
      provenance: "conversational_confirmed",
      writable: false,
      reason:
        "The recipient confirmed a readback. That is conversational evidence, not independent verification.",
    };
  }

  return {
    ...input,
    provenance: "spoken_only",
    writable: false,
    reason: "The value was spoken once and has not been independently checked.",
  };
}

export type VerifyAttempt = {
  observation: IdentifierObservation;
  typed: string;
  claimsSecondChannel: boolean;
};

export function applyHumanVerification(attempt: VerifyAttempt): IdentifierDecision {
  const typed = attempt.typed.trim();
  if (!attempt.claimsSecondChannel) {
    return classifyIdentifier({
      ...attempt.observation,
      secondChannelMatch: false,
    });
  }
  if (!typed) {
    return classifyIdentifier({
      ...attempt.observation,
      secondChannelMatch: false,
    });
  }

  const intended = attempt.observation.intended;
  if (intended && !identifiersEqual(typed, intended)) {
    return {
      ...classifyIdentifier({
        ...attempt.observation,
        extracted: typed,
        secondChannelMatch: false,
      }),
      provenance: "mismatch",
      writable: false,
      reason:
        "You typed a value that does not match the intended identifier. ExactRef will not write it.",
    };
  }

  return classifyIdentifier({
    ...attempt.observation,
    extracted: typed,
    intended: intended ?? typed,
    secondChannelMatch: true,
  });
}

export function provenanceLabel(value: Provenance): string {
  switch (value) {
    case "unknown":
      return "Unknown";
    case "spoken_only":
      return "Spoken only";
    case "conversational_confirmed":
      return "Readback confirmed — still unverified";
    case "mismatch":
      return "Mismatch — do not write";
    case "independently_verified":
      return "Independently verified";
  }
}
