# Upstream PRs from the feedback lab

## Upstream PRs opened 2026-09-14/15

Opened from Arshgill01 forks against `CALLE-AI/*` `main`. No live CALL-E call. No `run_call`. No real API key in tests.

| Repo | PR | Card | Summary |
| --- | --- | --- | --- |
| `calle-docs` | https://github.com/CALLE-AI/calle-docs/pull/60 | [XR-810](XR-810-hash-api-reference-goes-to-quickstart.md) | `#api-reference` (no slash) now redirects to API Reference instead of Quickstart |
| `call-e-integrations` | https://github.com/CALLE-AI/call-e-integrations/pull/136 | [XR-807](XR-807-post-calle-webhook-listed-as-api.md) | Drop customer `POST /calle/webhook` from the onboarding API table |
| `call-e-integrations` | https://github.com/CALLE-AI/call-e-integrations/pull/137 | [XR-808](XR-808-us-languages-include-indonesian.md) | US languages = English; Indonesia = English, Indonesian |
| `server-sdk-python` | https://github.com/CALLE-AI/server-sdk-python/pull/40 | [XR-806](XR-806-call-not-ready-aborts-wait.md) | `wait_for_result` keeps polling on `call_not_ready` |
| `server-sdk-python` | https://github.com/CALLE-AI/server-sdk-python/pull/41 | [XR-110](XR-110-python-recipients-skip-phone-alias.md) | `recipients=[{"phone": ...}]` gets the `phone`→`phones` alias |
| `server-sdk-typescript` | https://github.com/CALLE-AI/server-sdk-typescript/pull/26 | [XR-605](XR-605-create-and-wait-loses-call-id.md) | `createAndWait` attaches `callId`; fetch reject → `CalleConnectionError` |
| `call-e-integrations` | https://github.com/CALLE-AI/call-e-integrations/pull/138 | [XR-609](XR-609-call-status-hardcodes-call-started-true.md) | `calle call status` errors use `call_started: "unknown"` |
| `call-e-integrations` | https://github.com/CALLE-AI/call-e-integrations/pull/139 | [XR-604](XR-604-confirm-token-printed-to-stdout.md) | `call plan` redacts `confirm_token`; `--show-confirm-token` opt-in |

### Placement notes

- XR-807 and XR-808 live in the integrations root README (the onboarding API table and the regions table). `calle-docs` generates `/regions` from that README and must not edit generated `regions.mdx`. They were opened on `call-e-integrations`, not `calle-docs`.
- XR-810 is the only assigned card whose source is `calle-docs` (`zudoku.config.tsx`).
- Python #40 references issue #30 (same waiter) but does not implement wait-predicate or polling-argument parity. JSONDecodeError (#39) was not touched.
- TypeScript #26 does not claim to fix issues #17 or #23.

### Skipped as duplicate

None. `gh pr list` / `gh issue list` / search on 2026-09-14 showed no open PR for these symptoms. Nearby issues left alone: Python #30 / #39, TypeScript #17 / #23, integrations region issues 90 / 116 / 118 / 121.

### Tests

| PR | Result |
| --- | --- |
| Python #40, #41 | `pytest -q tests/test_calls.py` 9 passed; `ruff check` passed; `mypy src/calle` passed |
| TypeScript #26 | `pnpm test` 39 passed; `pnpm run typecheck` passed |
| Integrations #138, #139 | `pnpm --filter @call-e/cli test:unit` 61 passed, 1 skipped; `pnpm --filter @call-e/cli check` passed |
| Docs #60 | Playwright not run locally (needs full site build + Chromium). Spec updated for `/#api-reference`. |
| Docs #136, #137 | Documentation-only; branch-name check passed |

No unresolved test failures on the suites that were run.
