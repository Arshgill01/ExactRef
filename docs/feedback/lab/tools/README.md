# Docs feedback lab tools

Offline, reproducible checks for CALL-E developer docs. No `run_call`, no `calls.create` against a real recipient, no form submit, no Discord/GitHub writes, no tokens.

Expect a workdir at `/tmp/calle-lab` with:

- `calle-docs`, `call-e-integrations`, `server-sdk-typescript`, `server-sdk-python`
- `doc-*.md`, `doc-llms.txt`, `live-openapi.yaml`
- `venv` with `calle-ai==0.7.0`
- `tslab` with `@call-e/calle@0.7.0` and `@call-e/cli@0.5.1`

```bash
./docs/feedback/lab/tools/run_lab.sh
```

| Script | What it does |
| --- | --- |
| `extract_fences.py` | Pull fenced blocks from `calle-docs` + fetched `doc-*.md` |
| `check_samples.py` | `tsc --strict` / `py_compile` + unreachable-base run / curl vs OpenAPI / CLI `--help` flags |
| `crawl_links.py` | `curl` sitemap, internal/external links, `#fragments`, `.md` variants (system CA; Python urllib SSL fails on this host) |
| `check_consistency.py` | versions, timeouts, status enums, placeholders, Playwright pins, `llms.txt` vs sitemap |

Reports land in `/tmp/calle-lab/lab-out/` (`fences.json`, `sample-report.json`, `crawl-report.json`, `consistency-report.json`).
