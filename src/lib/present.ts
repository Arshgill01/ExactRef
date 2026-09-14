import { diffIdentifiers } from "./diff";
import type { CaseView } from "./cases";
import { exceptionForCase } from "./exceptions";
import type { BoardCase } from "@/components/Board";

export function toBoardCase(view: CaseView, siblings: CaseView[] = []): BoardCase {
  const intended = view.decision.intended ?? "";
  const extracted = view.decision.extracted ?? "";
  const cells = !intended && extracted
    ? [...extracted].map((ch) => ({ intended: null, extracted: ch, mark: "extra" as const }))
    : intended || extracted
      ? diffIdentifiers(intended, extracted)
      : [];
  const exception = exceptionForCase(view.id);
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
    exception: exception
      ? {
          id: exception.id,
          title: exception.title,
          purpose: exception.purpose,
          siblings: siblings
            .filter((item) => exception.caseIds.includes(item.id) && item.id !== view.id)
            .map((item) => ({
              id: item.id,
              title: item.title,
              fieldLabel: item.fieldLabel,
              provenance: item.decision.provenance,
            })),
        }
      : undefined,
  };
}
