# How to make ExactRef a better package

Research notes, 2026-09-13. ExactRef stays a write-gate, not another vertical desk.

## What already differentiates it

Public CALL-E agent repos lean toward ALLOW/BLOCK on a transcript, or a whole desk UI. ExactRef’s contract is narrower:

1. Character-level intended vs extracted (F/S, 0/O).
2. Readback-plus-yes is `conversational_confirmed`, never writable.
3. A human must type the value and claim a second channel.
4. The outbound task must not contain the intended identifier.
5. Wait honesty: `queued` + activity is not idle; local timeout is not hangup.

Keep that. Do not add analytics, CRM sync, or a second live-call product.

## What to add next (in order)

1. **CLI as the agent interface.** Done: `classify` / `verify` / `compile` print JSON and use exit `0` only for a writable decision. Agents should call this instead of re-implementing the rules in prose.
2. **Observation schema.** Done: `schemas/identifier-observation.json`. A host can validate before classify.
3. **Homophone fixtures.** FS-01 is the live F/S miss. FS-05 is 0/O. Next, only if needed: 1/I, B/D, M/N. Do not grow a catalog.
4. **Skill as protocol, board as host.** The awesome-repo PR should be `skills/exact-ref/` plus a link to this repo. The board is the dry-run, not the product.
5. **Publishable core later.** Split `src/lib/{provenance,diff,task,wait,mask,exactref-cli}.ts` as `@exactref/core` only after the skill is merged. Do not publish from a dirty hackathon tree.
6. **Optional classify-only MCP tool.** A tool that accepts an observation and returns a decision. It must not place calls, read tokens, or call `track_ui_events`.
7. **Webhook stance.** Unsigned CALL-E webhooks are not authority. If a host adds a receiver, re-fetch the stored call id with the API key before classify.

## What not to copy

- Transcript-wide ALLOW/BLOCK without an intended value. That hides one-character substitutions.
- Treating schema-valid + `task_completed` as a write.
- Auto-filling the verify box with the extracted value.
- A “confidence” score. Provenance is a named state.

## Package shape we want judges to see

```text
OH-01 (off-hire exception)
  → FS-01 / FS-02 (write-gates)
  → skill (rules) → CLI (machine) → board (fixture)
  → CALL-E PRs 128 / 129 (plumbing)
```

The CLI is how another agent uses ExactRef tomorrow. The board is how a judge sees F become S in one second. The docket is how the package holds together without reviving OffHire Desk.
