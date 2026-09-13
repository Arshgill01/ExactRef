export type TaskCompileInput = {
  purpose: string;
  fieldLabel: string;
  destinationLabel: string;
  factsTheAgentMayState: string[];
};

export type CompiledTask = {
  task: string;
  resultSchema: Record<string, unknown>;
  leaksIntended: boolean;
};

const LEAK_MARKERS = ["07198FECTIST", "INTENDED:", "expected identifier"];

export function compileIdentifierTask(input: TaskCompileInput): CompiledTask {
  const facts = input.factsTheAgentMayState.map((fact) => `- ${fact}`).join("\n");
  const task = [
    `Call ${input.destinationLabel}. Disclose that you are an automated assistant.`,
    `Purpose: ${input.purpose}`,
    `Ask for the ${input.fieldLabel} as one continuous string.`,
    "Do not interrupt while they speak. Wait for an end marker such as “that's all” or a two-second silence.",
    `Read the entire ${input.fieldLabel} back once. If they say no, ask them to repeat the whole string. Do not guess letters.`,
    "If a letter is ambiguous, ask for a word that starts with that letter. Do not substitute a similar-sounding letter.",
    "If they give a time or date that contradicts an earlier answer, leave both versions and do not pick one.",
    facts ? `You may state only these facts:\n${facts}` : "Do not volunteer identifiers, account numbers, or guessed values.",
    "Do not invent a confirmation number if they do not give one.",
  ].join("\n\n");

  return {
    task,
    resultSchema: {
      type: "object",
      additionalProperties: false,
      required: ["identifier", "readback_confirmed", "identifier_evidence"],
      properties: {
        identifier: {
          type: ["string", "null"],
          description: "The exact identifier as captured. Null if none was given.",
        },
        readback_confirmed: {
          type: "boolean",
          description: "True only if the recipient confirmed a full readback.",
        },
        identifier_evidence: {
          type: "string",
          description: "One verbatim recipient span that contains the identifier, or empty.",
        },
        unresolved_time: {
          type: ["string", "null"],
          description: "Leave contradictory times here. Do not resolve them in the summary.",
        },
      },
    },
    leaksIntended: LEAK_MARKERS.some((marker) => task.toUpperCase().includes(marker.toUpperCase())),
  };
}
