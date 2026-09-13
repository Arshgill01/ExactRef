/** Mask an identifier for logs and shared summaries. The review board does not use this. */
export function maskIdentifier(value: string): string {
  const trimmed = value.trim();
  if (trimmed.length <= 4) return trimmed;
  return `${"•".repeat(trimmed.length - 4)}${trimmed.slice(-4)}`;
}
