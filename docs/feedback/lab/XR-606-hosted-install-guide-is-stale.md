# XR-606 — The hosted installation guide teaches the exact `calle` usage the skills now forbid; its “More” links 404

New. 2026-09-14. Distinct from XR-204 (docs site missing MCP pages) and XR-709 (skills.sh vs repo skill drift). This is the `open.heycall-e.com` install guide, the first non-README link a judge follows.

## Finding

The Devpost/README onboarding chain links `https://open.heycall-e.com/.../install-guide.md` (hosted). The same document exists in the repo at `docs/install/CALL-E-installation-guide.md`. They have diverged: the repo copy was rewritten around `run-agent-command.mjs` + JSON `argv` (the fix shipped for issue 109 on Sep 8) and tells agents “Do not run `calle` directly.” The hosted copy still says `npm install -g @call-e/cli`, then run `calle auth login`, `calle call start` etc. as bare commands, and its footer links resolve to a 404.

A judge who follows the hosted guide installs a global binary the skills refuse to use, and gets the Cursor plugin's `run-agent-command.mjs` error path (“Unknown command”) when the skill later runs. This is the failure the Sep 8 fix was supposed to close.

## Surface / version / commit or URL

- Hosted: `https://open.heycall-e.com/.../install-guide.md` (fetched 2026-09-14, CRLF line endings)
- Repo: `call-e-integrations` `1ce9d77` `docs/install/CALL-E-installation-guide.md`
- `diff <(sed 's/\r//' install-guide.md) docs/install/CALL-E-installation-guide.md` → non-empty (exit 1)
- Skills on `1ce9d77`: “Run every CLI action through `run-agent-command.mjs` … never a bare `calle`”
- Footer “More” links in the hosted copy → HTTP 302 → 404 page

## Expected

One canonical install document, served from the repo at a stable URL, or a hosted copy regenerated on every release. Footer links resolve.

## Actual

Hosted (excerpt):

```text
npm install -g @call-e/cli
calle auth login
calle call start --goal "..." --phone-number <E164>
```

Repo (excerpt):

```text
node run-agent-command.mjs '{"argv":["auth","login"]}'
Do not run `calle` directly; always go through run-agent-command.mjs so the agent gets JSON envelopes.
```

Hosted footer: “More: <link>” → `302` → `404 Not Found` (two of two footer links).

## Evidence

- `/tmp/calle-lab/install-guide.md` (hosted fetch) vs `/tmp/calle-lab/call-e-integrations/docs/install/CALL-E-installation-guide.md`
- `curl -sIL` on the two footer URLs (final status 404)
- Skill grep for “run-agent-command.mjs” on `1ce9d77`

## Impact if an operator or agent trusted the current contract

First-10-minutes onboarding failure for anyone who arrives via the hosted link (which is the one on the public page). Also undoes the vendor's own issue-109 fix for those users. Judges on a fresh machine hit two different “how to run the CLI” stories before their first plan.

## Ask

Redirect the hosted URL to the raw repo file (or `docs.heycall-e.com/install`), add the guide to the release checklist, fix or remove the footer links.

## Do not claim

Refile of issue 109 (that issue is about the skill; this is the hosted doc). XR-204 / XR-709 as this card. Refile of 123/126/127.
