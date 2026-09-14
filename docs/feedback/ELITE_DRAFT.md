# Elite feedback draft (not submitted)

Deadline: 18 Sep 2026 23:45 SGT. One form per person. Judged on completeness, viability, impact.

Paste file: [PASTE_READY.md](PASTE_READY.md). Labs: [lab/](lab/). You fill: [USER_OWNED.md](USER_OWNED.md).

## Prize sentence

Four words for done and three objects named `result` teach an agent to write a schema-valid substitution as a fact and to dial again while GET still says `queued`. A 15-second MCP timeout plus a recover command will place that second call; GET will still look like a clean extract-miss when validation failed.

## What moved today (2026-09-14)

New, cited, paste-ready:

- XR-401 stitched “verbatim” evidence (same live call). Now Q-10 A.4.
- XR-402 events page = 100 rows, cursor, `queued` on `call.in_progress`. Now Q-10 A.5.
- XR-501 four nouns for “done.” Now Q-11 / Q-13.
- XR-502 / XR-503 / XR-504 (`result_schema`, three `result` objects, timeout ≠ hangup). Already in Q-11 / Q-13.
- XR-403 reframes A.1: extract equals last confirmed spoken form. Do not say CALL-E dropped an F.
- Surface matrix in `lab/ROLLUP-surfaces.md` (SDK, API, CLI, MCP, Cursor, skills.sh, ExactRef).

Docs lab (2026-09-14, live pages): XR-301 Playwright locks the Python-private cell; XR-302 live `queued` = “The call task is queued.”; XR-303 `timeoutMs: 120_000` ≠ hangup; XR-304 schema-valid overclaim; XR-305 extra-calls noon vs Rules 23:45 SGT; XR-306 changelog #158 ≠ issue 126. Folded into Q-11.

CLI/MCP lab (`lab/ROLLUP-cli-mcp.md`): XR-202 + XR-206 timeout/`recover` = second `run_call` → Q-10 D.9. XR-203 missing `ready_to_run` → Q-10 D.10. XR-204 docs MCP 404, XR-207 Time `start`/`end` vs `started_at` → Q-11. XR-201 / XR-205 stay in the lab (plan args / offset TTL); not pasted as new Q-10 bugs.

SDK/API lab (`lab/ROLLUP-sdk-api.md`): XR-107 validation invisible on GET → Q-10 E.11. XR-108 `--phone` × N recipients → Q-10 E.12. XR-109 Calls `--wait` exit 0 → Q-10 E.13. XR-110 Python `recipients[]` skip, XR-111 `cursor` vs `after`, XR-112 canceled=`call.failed`, XR-114 docs `context` absent → Q-11. XR-113 / XR-115 / XR-116 stay in the lab (Retry-After, webhook casing, E.164 min-length).

CONFIRMED only, not refiled: 126/127, gauntlet-001..007, XR-001..006, XR-401/402, XR-501..504, unsigned webhooks.

## OffHire

Desk is not the product. Exception `OH-01` is. Conversation-quality (interruption, “AI-like”) stays out of Q-10 unless it changes a write. FB-002 stays out. Stage of F/S is not isolated; do not say CALL-E dropped an F.

## Do not submit from an agent turn
