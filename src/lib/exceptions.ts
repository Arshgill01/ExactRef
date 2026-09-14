export type ExceptionRecord = {
  id: string;
  title: string;
  domain: "off_hire";
  purpose: string;
  facts: string[];
  caseIds: string[];
};

export const EXCEPTIONS: ExceptionRecord[] = [
  {
    id: "OH-01",
    title: "Reviewed return, supplier off-hire",
    domain: "off_hire",
    purpose:
      "One live English call on 2026-09-05 produced two values an operator would have written into a record.",
    facts: [
      "Pickup was arranged and not collected.",
      "The off-hire reference was read back and the recipient said yes.",
      "The collection time stayed contradictory in the structured field.",
      "The summary picked Sunday 5 PM anyway.",
    ],
    caseIds: ["FS-01", "FS-02"],
  },
];

export const CONTRIBUTIONS = [
  {
    id: "128",
    title: "calle mcp call treats tool isError as failure",
    href: "https://github.com/CALLE-AI/call-e-integrations/pull/128",
  },
  {
    id: "129",
    title: "Cursor skill reads result{} and marks output untrusted",
    href: "https://github.com/CALLE-AI/call-e-integrations/pull/129",
  },
] as const;

export function exceptionForCase(caseId: string): ExceptionRecord | undefined {
  return EXCEPTIONS.find((item) => item.caseIds.includes(caseId));
}

export function siblingsOf(caseId: string): string[] {
  const exception = exceptionForCase(caseId);
  return exception ? exception.caseIds.filter((id) => id !== caseId) : [];
}
