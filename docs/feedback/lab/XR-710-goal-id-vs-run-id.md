# XR-710 — Goal SDK exposes three ids; only one is valid on the poll path

## Finding

A Goal Run wire object has `id` (poll path), `run_id` (telephone / MCP member), and `call_id` (Calls API). The TypeScript SDK maps these to `GoalRun.id`, `.runId`, `.callId`. `goals.getRun` / `waitForResult` interpolate the **second argument** as `{goal_run_id}` in `GET /v1/goals/{goal_id}/runs/{goal_run_id}`. Passing `run.runId` or `run.callId` hits the wrong resource. MCP `get_call_run` wants the telephone `run_id`. An agent that “uses the run id” from the SDK object against the wrong surface 404s or polls a different call.

## Surface / version / commit or URL

- `@call-e/calle` source `2808e21` / npm `0.7.0` `src/goals.ts` `fromApiGoalRun` + `getRunWithSignal`
- OpenAPI `GoalRun` descriptions (same tree): do not substitute nested `run_id` for `GoalRun.id`
- MCP `get_call_run.inputSchema.run_id`: “Run identifier returned by `run_call`”

## Expected

One exported identifier for “poll this,” or methods named so `waitForResult(goalId, run.runId)` is a type error. Cross-links on the type: `/** not for GET .../runs/{goal_run_id} */`.

## Actual

Offline mapping of the SDK’s own test fixture shape:

```text
id      = rgrp_delivery_8472     → correct GET .../runs/rgrp_delivery_8472
runId   = run_delivery_8472      → GET .../runs/run_delivery_8472  (wrong)
callId  = calling_call_delivery_8472 → GET .../runs/calling_…     (wrong)
MCP get_call_run wants          run_delivery_8472
```

`fromApiGoalRun` (goals.ts):

```ts
id: run.id,
runId: run.run_id,
callId: run.call_id,
```

`getRunWithSignal` path params: `{ goal_id: goalId, goal_run_id: goalRunId }`.

SDK README says persist the idempotency key and that `waitForResult` returns when `result` or `error` is non-null; it does not say which property to pass as `goalRunId`.

## Evidence

`/tmp/calle-lab-ts/sdk/scripts/goal-id-mixup.mjs` (no network). `tests/goals.test.ts` fixture uses `id: "rgrp_delivery_8472"` and `run_id: "run_delivery_8472"`. OpenAPI comment: “Do not substitute the nested telephone `run_id`.”

## Impact if an operator or agent trusted the current contract

`const run = await client.goals.run(...)` then `waitForResult(run.goalId, run.runId)` because the property is named `runId` and MCP taught “poll with run_id.” That GET is not the Goal Run. The waiter times out or 404s; the agent creates another Goal Run (second call) or switches to MCP `get_call_run` with `run.id` (also wrong).

## Ask

Rename the SDK field to `telephoneRunId` (or similar) and require `waitForResult({ goalId, goalRunId: run.id })`. Add a compile-time branded type. One sentence on the Goal Runs page: three ids, three paths.

## Do not claim

A live 404 (offline proof only). XR-111 (cursor vs after). That MCP `run_id` equals Calls `call_id`.
