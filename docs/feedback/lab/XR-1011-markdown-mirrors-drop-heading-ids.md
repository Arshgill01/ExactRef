# XR-1011 — Markdown mirrors advertised in `llms.txt` drop heading ids

## Finding

`llms.txt` sends agents to `/calls.md`, `/goal-runs.md`, `/authentication.md`, …. HTML pages have Zudoku heading ids (`task-completion`, `call-status`, `sdk-examples`). The `.md` mirrors do not, except five explicit `<a id="…">` tags on Goal Runs.

Same-page markdown links such as `[Task completion](#task-completion)` therefore have no target on the file `llms.txt` told the agent to fetch. Cross-page links in those files correctly use HTML paths (`/calls#task-completion`) — those work in a browser, not in a raw `.md` viewer.

`llms-full.txt` concatenates the markdown and has the same missing hashes.

## Surface / version / commit or URL

- Live `/calls` HTML ids include `task-completion`, `call-status`, `recover-after-a-restart-or-lost-response`, `classify-the-final-endpoint`, `idempotency`
- Live `/calls.md`: no `id=` attributes; headings are plain `##`
- Live `/goal-runs.md` keeps only: `example-workflow`, `published-interface`, `create-a-run`, `schema-ownership`, `common-errors`
- Missing on that file: `sdk-examples` (the heading the HTML has)
- Crawl: `docs/feedback/lab/tools/crawl_links.py` `bad_fragments` (12), all on `.md` / `llms-full.txt`

## Expected

Either the `.md` mirrors would include the same `id`s as HTML, or `llms.txt` would link HTML and say hashes apply only there.

## Actual

```
# HTML
has task-completion True
# MD
MD has id attrs False
```

Goal Runs MD available ids: the five explicit anchors. `#sdk-examples` missing.

Observed: live HTML vs live markdown. Inferred: a markdown-only agent cannot jump to “Recover after a restart” even though Quickstart.md links that concept (it uses `/calls#…`, which the agent may rewrite to `/calls.md#…`).

## Evidence

`curl` of `/calls` vs `/calls.md`; crawl-report `bad_fragments`. Goal Runs MDX uses `<a id="create-a-run"></a>` for some sections and a bare `## SDK examples` for the one that 404s as a hash.

## Impact if an operator or agent trusted the current contract

The agent misses the recovery table and POSTs a replacement call after a lost create (the exact path the missing section forbids). Weaker than a wrong field name; it is how the recovery guidance becomes unreachable from the file `llms.txt` prefers.

## Ask

Emit heading ids into `publishMarkdown` output (or keep the explicit `<a id>` on every heading). Add `#sdk-examples` next to the other Goal Runs anchors. Point `llms.txt` at HTML if hashes will not exist on `.md`.

## Do not claim

- That `/calls#task-completion` fails in the HTML app (Playwright and this crawl both see the id).
- Refile of 109 / 123 / 126 / 127.
