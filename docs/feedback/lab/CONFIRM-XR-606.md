# CONFIRM-XR-606 — Hosted install guide still teaches `npm i -g` and bare `calle`

## Finding

Re-verified 2026-09-14 against the live hosted URL. New evidence: the fetched body still contains the stale steps. Not a new id.

## Surface / version / commit or URL

- Live https://open.heycall-e.com/document/mcp-archive/CALL-E-installation-guide.md (200, 2508 bytes)
- Repo copy `/tmp/calle-lab/call-e-integrations/docs/install/CALL-E-installation-guide.md` uses `run-agent-command.mjs` JSON argv and says not to run bare `calle`

## Expected

Hosted file would match the repo guide (launcher + `request.json`, no global npm).

## Actual

Live hosted extract:

```
The skill uses the local `calle` CLI. If `calle` is not already available,
install it:

```bash
npm install -g @call-e/cli
```

Verify the command:

```bash
env CALLE_SOURCE=skills_sh CALLE_INTEGRATION=skills_sh_skill CALLE_INTEGRATION_VERSION=0.1.0 calle --help
```
```

Observed: live body. This is the same class as XR-606 (footer/stale hosted vs repo).

## Evidence

`curl -sS` of the hosted URL, 2026-09-14, compared to the clone at `1ce9d77`-era `/tmp/calle-lab/call-e-integrations`.

## Impact if an operator or agent trusted the current contract

Unchanged: first-10-minutes agents install the colliding `calle` bin (issue 109 family — not refiled) and skip the launcher.

## Ask

Unchanged: redirect the hosted URL to the repo file; release checklist.

## Do not claim

- A refile of 109 / XR-701 (two `calle` bins) as a new card.
- Refile of 123 / 126 / 127.
