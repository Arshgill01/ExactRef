#!/usr/bin/env bash
# Reproducible CALL-E docs lab. No live create, no tokens, no form submit.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
LAB="${CALLE_LAB:-/tmp/calle-lab}"
OUT="${LAB}/lab-out"
mkdir -p "$OUT"

if [[ ! -x "${LAB}/venv/bin/python" ]]; then
  echo "missing ${LAB}/venv/bin/python" >&2
  exit 1
fi

if [[ ! -x "${LAB}/tslab/node_modules/.bin/calle" ]]; then
  echo "missing shipped CLI in ${LAB}/tslab" >&2
  exit 1
fi

# typescript + types for tsc --strict
if [[ ! -x "${LAB}/tslab/node_modules/typescript/bin/tsc" ]]; then
  (cd "${LAB}/tslab" && npm install --no-fund --no-audit typescript@5.9 @types/node@22)
fi

# mypy optional; py_compile always runs
if [[ ! -x "${LAB}/venv/bin/mypy" ]]; then
  "${LAB}/venv/bin/python" -m pip install -q mypy
fi

"${LAB}/venv/bin/python" "${ROOT}/extract_fences.py"
"${LAB}/venv/bin/python" "${ROOT}/check_samples.py"
"${LAB}/venv/bin/python" "${ROOT}/crawl_links.py"
"${LAB}/venv/bin/python" "${ROOT}/check_consistency.py"
echo "reports in ${OUT}"
