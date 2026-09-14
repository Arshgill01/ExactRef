import { Docket } from "@/components/Docket";
import { listCases } from "@/lib/cases";
import { EXCEPTIONS } from "@/lib/exceptions";

export default function HomePage() {
  const exception = EXCEPTIONS[0];
  const cases = listCases();
  const exceptionWrites = cases
    .filter((item) => exception.caseIds.includes(item.id))
    .map((item) => ({
      id: item.id,
      title: item.title,
      fieldLabel: item.fieldLabel,
      provenance: item.decision.provenance,
      writable: item.decision.writable,
    }));
  const otherWrites = cases
    .filter((item) => !exception.caseIds.includes(item.id))
    .map((item) => ({
      id: item.id,
      title: item.title,
      fieldLabel: item.fieldLabel,
      provenance: item.decision.provenance,
      writable: item.decision.writable,
    }));

  return (
    <Docket
      exception={exception}
      exceptionWrites={exceptionWrites}
      otherWrites={otherWrites}
    />
  );
}
