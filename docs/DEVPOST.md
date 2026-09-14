# Devpost submission — ExactRef

Paste-ready. Video: `~/Desktop/ExactRef-submission/ExactRef-pitch.mp4` (2:28) + `.srt`.

## Project name

ExactRef

## Tagline (≤ 60 chars)

Refuse to write a spoken CALL-E identifier as a fact.

## Links

- Awesome PR (required): https://github.com/CALLE-AI/awesome-phone-call-agents/pull/673
- Repository: https://github.com/Arshgill01/ExactRef
- Video: (YouTube link — fill after upload)
- Demo app: runs locally, see testing instructions. No hosted URL by design: the board must not be able to place a call from a public page.

## Text description

### Inspiration

On 2026-09-05 we placed one real CALL-E call (Calls API, Python SDK 0.7.0) to obtain a supplier off-hire reference. The recipient read it out, the agent read it back in full, the recipient said "yes". The `structured_result` came back schema-valid: `07198SECTIST`. The real reference was `07198FECTIST`. One character. Confirmed. Wrong.

Every agent integration we looked at would have written that value into a record, because "schema-valid + task_completed + the recipient said yes" is what they treat as truth. ExactRef exists to make that write impossible.

### What it does

ExactRef is the write-gate after a CALL-E call. It is not a calling desk.

- **Character-level check against an intended value.** Intended vs extracted are compared after normalising spaces, hyphens and case. The decision names the first differing character (`index 5: F → S`). F/S, 0/O, 1/I homophones are the same class.
- **Provenance is a named state, not a score.** `unknown`, `spoken_only`, `conversational_confirmed`, `mismatch`, `independently_verified`. Only the last is writable. Readback-plus-yes is `conversational_confirmed` — evidence, not verification.
- **Second-channel stamp.** To open the write a human must type the value from a written channel (email, portal, paper) and claim it. Typing the spoken (wrong) value keeps `mismatch`.
- **Task compiler that refuses to lead the call.** It compiles an outbound CALL-E task (one full readback, no interruptions, ask for a word for an ambiguous letter, leave contradictory times unresolved) and exits non-zero if the intended identifier leaks into the task text.
- **Wait honesty.** `queued` + attempt activity is not idle (do not create again); a local wait timeout is not hangup or cancel; `completed` without `structured_result` is not an extraction; MCP `COMPLETED` is not task success — read `result{}`.
- **`gate` for real CALL-E output.** Feed it a saved call object from REST, the Python/TypeScript SDK, `calle call status --json`, or the MCP `result{}` envelope. It refuses non-terminal calls, then classifies `structured_result[field]`.

### How we built it

- `skills/exact-ref/` — the Agent Skill (Claude Code, Codex, Cursor, OpenClaw, skills.sh): `SKILL.md`, `scripts/exactref.mjs` (one zero-dependency Node 18+ file: `classify` / `verify` / `compile` / `gate` / `fixtures`; exit `0` only when writable), fixtures including the live F/S call object, safety notes.
- Board (Next.js 15, React 19, TypeScript): a docket that groups the off-hire exception `OH-01` with its two blocked writes (`FS-01` reference, `FS-02` collection window) plus three other identifier classes. The identifier pair is the largest object on the page; provenance is text plus shape, never colour alone.
- Tests: vitest for the rules and parity between the standalone skill script and the board; Playwright e2e for the write-gate flow.
- Two upstream fixes to CALL-E from what we hit while building: [call-e-integrations#128](https://github.com/CALLE-AI/call-e-integrations/pull/128) (`calle mcp call` treats tool `isError` as failure) and [call-e-integrations#129](https://github.com/CALLE-AI/call-e-integrations/pull/129) (Cursor skill reads `result{}` and marks tool output untrusted).
- A feedback lab (`docs/feedback/lab/`) of verified, reproducible findings across the Python/TypeScript SDKs, CLI, MCP server, and docs, each with one concrete ask.

### Challenges

- Isolating the F/S stage is not possible from outside CALL-E, so the skill refuses to guess: it compares against the intended value rather than blaming ASR or the LLM.
- Top-level `queued` during an active attempt, a 15-second MCP `call` timeout, and `recover` re-sending `run_call` all make a second dial easy. Wait honesty is a rule set, not a UI hint.
- Keeping the package to one product. Off-hire is a proof exception (`OH-01`), not a second desk.

### What we learned

Schema validation checks shape. Readback checks the transcript. Neither checks the fact. The only thing that does is a second channel and a human who types.

### What's next

Classify-only MCP tool (accepts an observation, returns a decision, never dials). `@exactref/core` once the skill is merged. More homophone fixtures only if a real call produces one.

### Significant updates during the Submission Period

Everything here was created during the Submission Period (first commit 2026-09-13).

## Testing instructions (for judges)

No credentials, no calls.

```bash
git clone https://github.com/Arshgill01/ExactRef && cd ExactRef

# 10-second check: the live miss is blocked, exit 2, mismatch at character 6
node skills/exact-ref/scripts/exactref.mjs classify --intended 07198FECTIST --extracted 07198SECTIST --readback

# Gate a saved CALL-E call object
node skills/exact-ref/scripts/exactref.mjs gate --call skills/exact-ref/references/call-fs01.json --intended 07198FECTIST

# Human types the value from a second channel → independently_verified, exit 0
node skills/exact-ref/scripts/exactref.mjs verify --intended 07198FECTIST --extracted 07198SECTIST --typed 07198FECTIST --second-channel

# Board
npm install && npm test && npm run dev    # http://127.0.0.1:3450 → OH-01 → FS-01
```

On FS-01: type `07198SECTIST`, tick the second-channel box, click "Mark independently verified" — still `Mismatch — do not write`. Type `07198FECTIST` — `Independently verified`, writable yes. "Place live call" opens a dialog saying live create is disabled.

## Built with

TypeScript, Node.js, Next.js, React, Vitest, Playwright, CALL-E Calls API, CALL-E Python SDK, CALL-E CLI/MCP.

## CALL-E account email

(user fills)
