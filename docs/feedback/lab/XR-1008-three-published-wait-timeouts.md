# XR-1008 — Three published Calls wait timeouts: 120s, 300s, 600s

## Finding

The same Calls waiter is documented with three different numbers on the official docs host:

| Surface | Value |
| --- | --- |
| Calls / SDKs guide samples | `timeoutMs: 120_000` / `timeout_seconds=120` |
| Official complete example `examples/calls.py` | `timeout_seconds=300` |
| Python SDK 0.7.0 default | `timeout_seconds: float = 600.0` |
| TypeScript SDK 0.7.0 | `WaitOptions.timeoutMs` optional; runtime default is the same 600s class (XR-303) |

XR-303 already owns “120s example ≠ hangup / default 600s.” This card is the **third published number** in the Quickstart-linked complete example, which Quickstart itself describes as a five-minute polling timeout. The guide samples next to it still say 120 seconds.

Not XR-712 (MCP `get_call_run` poll cadence).

## Surface / version / commit or URL

- `calle-docs/content/guides/calls.mdx` / `sdks.mdx` wait samples
- Live `/quickstart.md`: “five-minute polling timeout”
- `calle-docs/examples/calls.py` `wait_for_result(call_id, timeout_seconds=300)`
- `calle-ai==0.7.0` `calle/calls.py` `timeout_seconds: float = 600.0`

## Expected

One number in the guides, the complete example, and the SDK default — or a sentence that 120 / 300 are local poll budgets, not server limits, and that omitting the option waits 600s.

## Actual

Quickstart prose: five minutes. Example code: 300s. Adjacent Calls/SDK fences: 120s. Client default if you omit the kwarg: 600s.

Observed: the four sources. Inferred: an agent that copies the guide fence gives up at 2 minutes and POSTs again (XR-303 path); one that copies `calls.py` waits 5 minutes; one that calls `wait_for_result(id)` with no args waits 10.

## Evidence

Grep of the three files. `python -m py_compile examples/calls.py` OK.

## Impact if an operator or agent trusted the current contract

Same as XR-303’s duplicate-create path, plus “the official complete example disagreed with the fence I copied” support noise. A live result in this repo took longer than 120s (cited in XR-303).

## Ask

Pick one documented poll budget (or “omit to use 600s”). Make the complete example and the guide fences match. Keep the “timeout does not cancel” sentence from XR-303.

## Do not claim

- A new live wait measurement this turn.
- A refile of XR-303 / XR-504 (timeout ≠ hangup) except as the 120 vs 600 half of this table.
- A refile of XR-712 (MCP cadences).
- Refile of 109 / 123 / 126 / 127.
