# XR-811 — Generated `GoalRun.created_at` is `datetime`; `CalleClient.goals` returns an ISO string

## Finding

One package, two clocks. `GoalRun.from_dict` parses `created_at` / `completed_at` as `datetime.datetime`. `CalleClient.goals.get_run` / `wait_for_result` return the raw JSON strings. Docs Python samples treat Goal runs as dicts of strings (`run["id"]`, ISO timestamps). An operator who “upgrades” a wrapper dict through `GoalRun.from_dict` changes the type under the same field name.

Calls have no generated `CallTask`, so this split exists only on Goals today (see XR-801).

## Surface / version / commit or URL

- PyPI `calle-ai==0.7.0` / git `9f69e4a`
- `src/calle/generated/models/goal_run.py` `created_at: datetime.datetime`
- `src/calle/goals.py` `_request` → `response.json()` dict
- https://docs.heycall-e.com/goal-runs.md Python examples use `run["id"]` dict access

## Expected

Both surfaces would use one type (ISO strings, matching REST, or datetime). Docs would say which.

## Actual

Generated model docstring: “UTC time at which CALL-E durably accepted this Goal Run” typed as `datetime.datetime`.

Wrapper: no parse step.

## Evidence

`prove_sdk_bugs.py` `test_goalrun_from_dict_datetime_vs_wrapper_str`:

```
payload["created_at"] = "2026-07-22T10:00:00Z"
GoalRun.from_dict(payload).created_at → datetime
client.goals.get_run(...)["created_at"] → str == "2026-07-22T10:00:00Z"
```

`goal_run.py` attributes `created_at` / `completed_at` as quoted in the generated class.

No live Goal Run.

## Impact if an operator or agent trusted the current contract

`created_at.isoformat()` on a wrapper dict raises `AttributeError` (`str` has no `isoformat` in that style if they thought it was datetime — actually str has no issue if they treat it as str). The failure is the mixed path: `model.created_at == run["created_at"]` is False (`datetime` vs `str`), so idempotency / “same run” checks fail and the agent starts a new Run with a new key. Inferred: we did not run a live duplicate. Observed: the types differ on the same payload.

Timezone: `datetime.fromisoformat("...Z")` is UTC-aware on 3.11+; printing it without `timespec` can drop `Z`. CLI localize uses `started_at` strings (XR-207, do not refile).

## Ask

Pick one: wrapper parses through `GoalRun.from_dict` and returns the model, or generated fields stay `str`. Document it on /goal-runs next to the snake/camel table.

## Do not claim

- A live Goal Run.
- Refile of XR-207 (`started_at` vs `start` in Cursor).
- Refile of 109 / 123 / 126 / 127.
