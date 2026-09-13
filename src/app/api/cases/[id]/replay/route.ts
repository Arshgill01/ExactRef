import { NextResponse } from "next/server";
import { replayCase } from "@/lib/cases";

export async function POST(_request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  const view = replayCase(id);
  if (!view) return NextResponse.json({ error: "Unknown case." }, { status: 404 });
  return NextResponse.json({ id: view.id, provenance: view.decision.provenance });
}
