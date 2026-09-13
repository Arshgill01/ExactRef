import { notFound } from "next/navigation";
import { Board } from "@/components/Board";
import { listCases, viewCase } from "@/lib/cases";
import { toBoardCase } from "@/lib/present";

export default async function CasePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const current = viewCase(id);
  if (!current) notFound();
  return <Board cases={listCases().map(toBoardCase)} current={toBoardCase(current)} />;
}
