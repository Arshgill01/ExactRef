import { NextResponse } from "next/server";
import { verifyCase } from "@/lib/cases";

export async function POST(request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  const body = (await request.json().catch(() => null)) as
    | { typed?: unknown; claimsSecondChannel?: unknown }
    | null;
  const typed = typeof body?.typed === "string" ? body.typed : "";
  const claimsSecondChannel = body?.claimsSecondChannel === true;
  if (!claimsSecondChannel) {
    return NextResponse.json(
      { error: "A second channel claim is required. A spoken yes is not enough." },
      { status: 400 },
    );
  }
  if (!typed.trim()) {
    return NextResponse.json({ error: "Type the identifier from the written channel." }, { status: 400 });
  }
  const view = verifyCase(id, typed, claimsSecondChannel);
  if (!view) return NextResponse.json({ error: "Unknown case." }, { status: 404 });
  return NextResponse.json({
    id: view.id,
    provenance: view.decision.provenance,
    writable: view.decision.writable,
    reason: view.decision.reason,
  });
}
