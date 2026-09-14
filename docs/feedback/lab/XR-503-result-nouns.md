# XR-503 — three objects named `result`, two templates

## Finding

`result` means three different objects. Shipped Cursor 0.1.2 and skills.sh `SKILL.md` read summary at the top level. skills.sh `references/commands.md` and issue 126 put it under nested `result{}`. An agent cannot satisfy both files.

## Surface / version / commit or URL

- MCP guide: JSON-RPC `response.result` is `CallToolResult`; prose also says the tool “can include … summary”
- CLI: actionable object is `result.structuredContent`
- Issue 126: `get_call_run` identifier/summary/transcript under nested `result{}` on COMPLETED
- Cursor shipped 0.1.2 `4a53b01`: `<post_summary or summary or message>` (no `result.` prefix)
- skills.sh 0.1.0: SKILL.md top-level template; `commands.md` `result.summary`
- ExactRef: “MCP summaries live under `result{}`.”

## Expected

One path, one noun. The skill template matches the live envelope.

## Actual

An agent that follows shipped Cursor or skills.sh SKILL.md writes from a top-level `summary` that can be empty on `COMPLETED`. Local Cursor `560d61c` (still labeled 0.1.2) reads `result.summary`. Published plugin does not.

## Impact

Empty top-level on COMPLETED → invent a summary or scrape transcript prose, then treat that as the identifier. Same write-wrong path as XR-501.

## Ask

One sentence on the MCP guide and both skill templates: `get_call_run` summary/transcript are `result.summary` / `result.transcript`. JSON-RPC `response.result` is the tool wrapper. CLI `result.structuredContent` is that wrapper. Cite 126; do not refile it.

## Do not claim

Not a new filing of 126. Local PR 129 is a proposed fix, not the published plugin.
