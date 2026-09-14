# XR-606 — The hosted “Install CALL-E for me” guide teaches `npm install -g` + bare `calle`; the repo copy and the skill forbid both; its footer links land on 404

New. 2026-09-14 (re-verified 21:50 IST). Distinct from XR-204 (docs site missing MCP pages) and XR-701 (two packages install `calle`; issue 109 family — not refiled). This is the hosted install document that the README hands to agents as the stable installation prompt.

## Finding

`call-e-integrations` README (lines 30 and 126 on `1ce9d77`) tells users to paste into their agent:

```text
Install CALL-E for me: https://open.heycall-e.com/document/mcp-archive/CALL-E-installation-guide.md
```

The same document lives in the repo at `docs/install/CALL-E-installation-guide.md`. The two have diverged. The hosted copy (MD5 `9b6fb93f…`, identical on two fetches 2026-09-14) still says:

```text
The skill uses the local `calle` CLI. If `calle` is not already available, install it:
    npm install -g @call-e/cli
Verify the command:
    env CALLE_SOURCE=skills_sh CALLE_INTEGRATION=skills_sh_skill CALLE_INTEGRATION_VERSION=0.1.0 calle --help
...
    env ... calle auth login
    env ... calle auth status
    env ... calle mcp tools
```

The repo copy at `1ce9d77` replaced Step 2 with:

```text
Follow CLI entry point selection (../../packages/cli/docs/cli-reference.md#selecting-the-cli-entry-point)
to select the trusted MCP package and prepare the launcher and `request.json`.
The JSON arrays below are values for that request's `argv`; execute them one
at a time with `node run-agent-command.mjs request.json`.
... the skill does not download remote npm packages.
```

and every command is a JSON `argv` array (`["auth", "login"]`, `["auth", "status"]`, `["mcp", "tools"]`).

The skill the guide installs in Step 1 (skills.sh `skills/calle/SKILL.md` 0.1.0, `1ce9d77`) says:

```text
43: Run every CLI command through the bundled `scripts/run-agent-command.mjs`.
47: Do not run bare `calle` or use `npx` to select the CLI.
```

So an agent that follows the hosted prompt literally installs a global binary and verifies it with bare `calle …` commands the skill it just installed refuses to use, and never creates the `request.json` / launcher the skill requires.

The hosted footer (“## More”) links `./install-guide.md` and `./cli.md`; both resolve (HTTP 200 after redirect) to `https://open.heycall-e.com/404.html`.

## Surface / version / commit or URL

- Hosted: `https://open.heycall-e.com/document/mcp-archive/CALL-E-installation-guide.md` (fetched 2026-09-14 ~13:30 UTC and ~16:20 UTC; CRLF; identical)
- Repo: `call-e-integrations` `1ce9d77` `docs/install/CALL-E-installation-guide.md`, `README.md:30,126`, `skills/calle/SKILL.md:43,47`
- `diff <(sed 's/\r//' install-guide.md) docs/install/CALL-E-installation-guide.md` → non-empty (Step 2 and all command blocks)
- Footer: `curl -sSL -o /dev/null -w '%{url_effective}'` → `https://open.heycall-e.com/404.html` for both links

## Expected

One canonical install document: the hosted URL serves the repo file (or redirects to it), and is regenerated on release. Footer links resolve.

## Actual

As quoted. Hosted = pre-launcher text (global install, bare `calle`). Repo = launcher text. Skill = launcher-only. Footer = 404 page.

## Evidence

- `/tmp/calle-lab/install-guide.md` (hosted fetch) vs `/tmp/calle-lab/call-e-integrations/docs/install/CALL-E-installation-guide.md`
- `curl` final-URL checks above
- `rg -n "run-agent-command|bare" skills/calle/SKILL.md` on `1ce9d77`

## Impact if an operator or agent trusted the current contract

First-ten-minutes onboarding failure for everyone who uses the README's own “Install CALL-E for me” line: two contradictory instructions for how to run the CLI before the first plan, and a skill whose rule is “if no trusted installation is available, stop and ask the user to install or update `@call-e/cli`” (SKILL.md:55–56) — whether a global install counts as trusted is not stated (inferred). The hosted text also reintroduces the global-install path the launcher work was meant to replace.

## Ask

Serve the repo file at the hosted URL (redirect or CI publish on release); fix or remove the two footer links; add the hosted URL to the release checklist.

## Do not claim

Refile of issue 109 (that issue is about the binary collision; this is the hosted document). XR-204 as this card. Refile of 123/126/127.
