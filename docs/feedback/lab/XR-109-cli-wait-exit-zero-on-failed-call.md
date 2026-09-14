# XR-109 — CLI `--wait` exits 0 on a failed or canceled Call

## Finding

Goal CLI wait treats a domain `error` as process failure (exit 1). Call CLI wait treats `failed` and `canceled` as success (exit 0) and prints the row. Scripts that use `calle calls create --wait` will proceed as if the task succeeded.

## Surface / version / commit or URL

TypeScript `@call-e/calle@0.7.0` `36ee6f1` `src/cli.ts`. Library `waitForResult` is documented to return failed calls (tests lock this). The **CLI** never maps that to a nonzero exit.

## Expected

`--wait` on Calls would fail the process when `status` is `failed` or `canceled`, matching `failOnGoalRunError`. At minimum, non-JSON mode would not look like `id\tcompleted`.

## Actual

```277:281:src/cli.ts
function failOnGoalRunError(run: GoalRun): void {
  if (run.error !== null) {
    throw new Error(`Goal Run ${run.id} failed: ${run.error.message} (${run.error.code}).`);
  }
}
```

```302:304:src/cli.ts
function isTerminalCall(call: Call): boolean {
  return call.status === "completed" || call.status === "failed" || call.status === "canceled";
}
```

`waitForCallResult` returns that Call. `runCreate` prints it and `runCalleCli` returns `0`. There is no `failOnCallError`.

Tests: Goal wait with `error` expects exit 1 (`tests/cli.test.ts` “returns an error exit code when a waited Goal Run has a domain error”). No equivalent for a failed Call.

Library (intentional): `tests/calls.test.ts` “returns failed terminal calls instead of throwing.”

## Evidence

- `server-sdk-typescript/src/cli.ts:277-281`, `302-304`, `336-374`, `376-394`, `426-444`
- `server-sdk-typescript/tests/cli.test.ts:284-328` (Goal exit 1)
- `server-sdk-typescript/tests/calls.test.ts:155-168` (library returns failed)

## Impact if an operator or agent trusted the current contract

`calle calls create --wait && write_crm` commits a failed or canceled task. JSON mode still exits 0; only `status` in the body tells the truth. Goal operators already get exit 1, so a dual-surface script is inconsistent.

## Ask

After `waitForCallResult`, if `status !== "completed"` (or if `failureCode` is set), exit 1 the same way Goals do. Keep library `waitForResult` returning the Call.

## Do not claim

- A live failed CLI run this session.
- That library `waitForResult` should throw (tests say it must not).
- Timeout-is-not-hangup (XR-504 / gauntlet-004).
- Refile of 109 / 123 / 126 / 127.
