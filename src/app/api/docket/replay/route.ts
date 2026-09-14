import { NextResponse } from "next/server";
import { replayAllCases } from "@/lib/cases";

export async function POST() {
  const cases = replayAllCases();
  return NextResponse.json({ replayed: cases.map((item) => item.id) });
}
