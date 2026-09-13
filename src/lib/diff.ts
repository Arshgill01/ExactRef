export type DiffMark = "same" | "changed" | "missing" | "extra";

export type DiffCell = {
  intended: string | null;
  extracted: string | null;
  mark: DiffMark;
};

export function normalizeIdentifier(value: string): string {
  return value.replace(/[\s\-_.]/g, "").toUpperCase();
}

export function identifiersEqual(a: string, b: string): boolean {
  return normalizeIdentifier(a) === normalizeIdentifier(b);
}

/** Index-align when lengths match; otherwise walk both strings. */
export function diffIdentifiers(intended: string, extracted: string): DiffCell[] {
  if (intended.length === extracted.length) {
    return [...intended].map((ch, i) => {
      const other = extracted[i] ?? null;
      return {
        intended: ch,
        extracted: other,
        mark: ch === other ? "same" : "changed",
      };
    });
  }

  const cells: DiffCell[] = [];
  let i = 0;
  let j = 0;
  while (i < intended.length || j < extracted.length) {
    const a = intended[i] ?? null;
    const b = extracted[j] ?? null;
    if (a === b) {
      cells.push({ intended: a, extracted: b, mark: "same" });
      i += 1;
      j += 1;
      continue;
    }
    if (a && !b) {
      cells.push({ intended: a, extracted: null, mark: "missing" });
      i += 1;
      continue;
    }
    if (b && !a) {
      cells.push({ intended: null, extracted: b, mark: "extra" });
      j += 1;
      continue;
    }
    cells.push({ intended: a, extracted: b, mark: "changed" });
    i += 1;
    j += 1;
  }
  return cells;
}

export function firstMismatchIndex(cells: DiffCell[]): number | null {
  const index = cells.findIndex((cell) => cell.mark !== "same");
  return index === -1 ? null : index;
}
