# ExactRef — recommended CALL-E submission

**Decision, 2026-09-14.** Do not submit OffHire Desk or WindowCrew as products. Submit ExactRef as one package: off-hire exception `OH-01` → write-gate → `skills/exact-ref/` → CLI → CALL-E PRs. Target: reusable contribution (Quality of the Idea) and Most Valuable Feedback. Practical $4,000 is secondary.

Deadline: project PR + Devpost + video by **14 September 2026, 21:15 IST**. Feedback survey open through **18 September 2026, 23:45 SGT**.

## Why this and not another desk

awesome-phone-call-agents is flooded with vertical apps and skills. OffHire Desk was that shape: queue, bench, multi-model theater. That is why it is not the product. The off-hire *call* is still the only live proof we own, so the package keeps it as exception `OH-01` (two blocked writes) instead of rebuilding the desk. WindowCrew’s skill talks to an app HTTP API, not CALL-E. Judges score reusability. Derek @ CALL-E explicitly allowed a standalone skill.

## Package

1. **Devpost / awesome PR:** `skills/exact-ref/` — when an agent must obtain an exact operational identifier over the phone, compile a readback protocol, then treat `structured_result` as `spoken_only` until a second channel or human verifies it. The local board and `exactref` CLI are the dry-run. See [PACKAGE_RESEARCH.md](PACKAGE_RESEARCH.md).
2. **CALL-E infra PRs:** [call-e-integrations#128](https://github.com/CALLE-AI/call-e-integrations/pull/128) (`calle mcp call` + `isError`) and [call-e-integrations#129](https://github.com/CALLE-AI/call-e-integrations/pull/129) (Cursor skill `result{}` envelope + untrusted boundary).
3. **Feedback survey + Discord** using [docs/feedback/PASTE_READY.md](feedback/PASTE_READY.md).

## Evidence we already own

- One live Calls API / Python SDK 0.7.0 call, 2026-09-05: intended `07198FECTIST`, extracted `07198SECTIST` after readback + yes. Top-level `queued` during an active attempt. Summary resolved a contradictory time. See OffHire `docs/research/LIVE_CALL_FINDINGS.md`.
- Tonight (2026-09-13): usable CLI login; `calle mcp tools` returned four tools including undocumented `track_ui_events`; Cursor skill vs skills.sh drift; generic `calle mcp call` still `ok: true` on `isError`; Python repo public vs docs “not public”; dates table still missing Feedback Period.

## What we have not done

No second live call. No form submit. No Discord post. No awesome PR. SKILL checkbox stays unchecked until the ExactRef skill is actually invoked.
