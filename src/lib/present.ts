import { diffIdentifiers } from "./diff";
import type { CaseView } from "./cases";
import type { BoardCase } from "@/components/Board";

export function toBoardCase(view: CaseView): BoardCase {
  const intended = view.decision.intended ?? "";
  const extracted = view.decision.extracted ?? "";
  const cells = !intended && extracted
    ? [...extracted].map((ch) => ({ intended: null, extracted: ch, mark: "extra" as const }))
    : intended || extracted
      ? diffIdentifiers(intended, extracted)
      : [];
  return {
    id: view.id,
    title: view.title,
    fieldLabel: view.fieldLabel,
    destinationLabel: view.destinationLabel,
    summary: view.summary,
    waitNote: view.waitNote,
    decision: view.decision,
    task: { task: view.task.task, leaksIntended: view.task.leaksIntended },
    cells,
  };
}
