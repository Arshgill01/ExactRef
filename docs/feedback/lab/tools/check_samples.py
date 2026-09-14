#!/usr/bin/env python3
"""Compile/typecheck docs samples offline against published 0.7.0 packages.

Never calls the live API with a real recipient. Python runtime uses a fake
API key and an unreachable base URL. TypeScript uses tsc --noEmit --strict.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LAB = Path("/tmp/calle-lab")
OUT = LAB / "lab-out"
VENV_PY = LAB / "venv" / "bin" / "python"
TSLAB = LAB / "tslab"
CALLE = TSLAB / "node_modules" / ".bin" / "calle"
OPENAPI = LAB / "live-openapi.yaml"

TS_PREAMBLE = """\
import { CalleClient } from "@call-e/calle";

declare const process: { env: Record<string, string | undefined> };
declare const rawBody: Buffer;
declare const request: { headers: { get(name: string): string | null } };
declare const eventStore: { has(id: string): Promise<boolean>; insert(id: string): Promise<void> };
declare function handleCallEvent(payload: unknown): Promise<void>;
declare const console: { log(...args: unknown[]): void };

const client = new CalleClient({
  apiKey: process.env.CALLE_API_KEY ?? "iams_lab_fake",
});
const labCall = {
  id: "call_lab",
  status: "completed" as const,
  structuredResult: null as Record<string, unknown> | null,
  taskCompleted: true as boolean | null,
  completionConfidence: null,
  evidence: [] as string[],
  recipients: [] as unknown[],
};
void labCall;
"""

PY_PREAMBLE = """\
import json
import os
from calle import CalleClient

client = CalleClient(api_key=os.environ.get("CALLE_API_KEY", "iams_lab_fake"), base_url="http://127.0.0.1:1")
call = {"id": "call_lab", "status": "completed", "structured_result": None, "task_completed": True, "completion_confidence": None, "evidence": []}
raw_body = b"{}"
class _H(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)
request = type("R", (), {"headers": _H()})()
event = {"id": "evt_lab", "type": "call.completed", "data": {"id": "call_lab", "recipients": []}}
class _Store:
    def has(self, _id):
        return False
    def insert(self, _id):
        return None
event_store = _Store()
def handle_call_event(event):
    return None
"""

FRAGMENT_START = re.compile(
    r"^(resultSchema|recipientResultSchema|result_schema|recipient_result_schema)\s*:"
)


def load_fences() -> list[dict]:
    return json.loads((OUT / "fences.json").read_text(encoding="utf-8"))


def classify_ts(body: str) -> str:
    stripped = body.strip()
    if FRAGMENT_START.match(stripped):
        return "fragment"
    if "import " in stripped or stripped.startswith("const client") or stripped.startswith("import{"):
        return "complete"
    if "client." in stripped or "console.log(call." in stripped or "await client" in stripped:
        return "continuation"
    if "JSON.parse" in stripped or "eventStore" in stripped or "event.id" in stripped:
        return "handler_fragment"
    return "fragment"


def classify_py(body: str) -> str:
    stripped = body.strip()
    if stripped.startswith("from calle") or stripped.startswith("import os"):
        return "complete"
    if "client." in stripped or 'call["' in stripped or "print(call" in stripped:
        return "continuation"
    if "json.loads" in stripped or "event_store" in stripped or "event[" in stripped:
        return "handler_fragment"
    return "fragment"


def wrap_ts(sample: dict) -> str:
    body = sample["body"]
    kind = classify_ts(body)
    if kind == "complete":
        src = body
        if "process.env" in src and "declare const process" not in src:
            src = "declare const process: { env: Record<string, string | undefined> };\n" + src
        return src
    if kind == "fragment":
        return "const _docExample = {\n" + body + "\n};\n"
    if kind == "handler_fragment":
        return TS_PREAMBLE + "\nasync function _labHandler() {\n" + body + "\n}\nvoid _labHandler;\n"
    rewritten = body
    # Continuation samples often use `call` from the previous fence.
    if re.search(r"\bcall\.", rewritten) and not re.search(r"\bconst call\b|\blet call\b", rewritten):
        rewritten = re.sub(r"\bcall\b", "labCall", rewritten)
    return TS_PREAMBLE + "\n" + rewritten + "\n"


def wrap_py(sample: dict) -> str:
    body = sample["body"]
    kind = classify_py(body)
    if kind == "complete":
        return body
    if kind == "handler_fragment":
        return PY_PREAMBLE + "\ndef _lab_handler():\n" + "".join(
            "    " + line + "\n" for line in body.splitlines()
        )
    return PY_PREAMBLE + "\n" + body + "\n"


def run_cmd(argv: list[str], cwd: Path | None = None, env: dict | None = None, timeout: int = 30) -> dict:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    try:
        proc = subprocess.run(
            argv,
            cwd=cwd,
            env=merged,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "argv": argv,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "argv": argv,
            "returncode": 124,
            "stdout": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr": f"timeout after {timeout}s",
        }


def check_typescript(samples: list[dict]) -> list[dict]:
    ts_samples = [s for s in samples if s["lang"] in {"typescript", "javascript"}]
    work = Path(tempfile.mkdtemp(prefix="calle-ts-samples-"))
    shutil.copytree(TSLAB / "node_modules", work / "node_modules", symlinks=True)
    (work / "package.json").write_text(
        json.dumps({"type": "module", "dependencies": {"@call-e/calle": "0.7.0"}}),
        encoding="utf-8",
    )
    (work / "tsconfig.json").write_text(
        json.dumps(
            {
                "compilerOptions": {
                    "target": "ES2022",
                    "module": "NodeNext",
                    "moduleResolution": "NodeNext",
                    "strict": True,
                    "noEmit": True,
                    "skipLibCheck": True,
                    "types": ["node"],
                    "lib": ["ES2022"],
                },
                "include": ["samples/**/*.ts"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    sample_dir = work / "samples"
    sample_dir.mkdir()
    rows = []
    tsc = work / "node_modules" / "typescript" / "bin" / "tsc"
    if not tsc.exists():
        tsc = Path(shutil.which("tsc") or "")
    for sample in ts_samples:
        kind = classify_ts(sample["body"])
        wrapped = wrap_ts(sample)
        name = f"s{sample['index']:02d}_{Path(sample['source']).stem}.ts"
        path = sample_dir / name
        path.write_text(wrapped + "\n", encoding="utf-8")
        result = run_cmd(
            [
                str(tsc),
                "--pretty",
                "false",
                "--strict",
                "--noEmit",
                "--target",
                "ES2022",
                "--module",
                "NodeNext",
                "--moduleResolution",
                "NodeNext",
                "--skipLibCheck",
                "--lib",
                "ES2022",
                str(path),
            ],
            cwd=work,
        )
        errors = [
            line
            for line in (result["stdout"] + "\n" + result["stderr"]).splitlines()
            if "error TS" in line
        ]
        rows.append(
            {
                "id": sample["id"],
                "source": sample["source"],
                "start_line": sample["start_line"],
                "lang": sample["lang"],
                "kind": kind,
                "pass": result["returncode"] == 0,
                "errors": errors[:12],
                "returncode": result["returncode"],
            }
        )
    (OUT / "ts-work-dir.txt").write_text(str(work), encoding="utf-8")
    return rows


def check_python(samples: list[dict]) -> list[dict]:
    py_samples = [s for s in samples if s["lang"] == "python"]
    work = Path(tempfile.mkdtemp(prefix="calle-py-samples-"))
    rows = []
    pyright = shutil.which("pyright")
    mypy = LAB / "venv" / "bin" / "mypy"
    for sample in py_samples:
        kind = classify_py(sample["body"])
        raw_path = work / f"raw_{sample['index']:02d}_{Path(sample['source']).stem}.py"
        wrap_path = work / f"wrap_{sample['index']:02d}_{Path(sample['source']).stem}.py"
        raw_path.write_text(sample["body"] + "\n", encoding="utf-8")
        wrap_path.write_text(wrap_py(sample) + "\n", encoding="utf-8")
        compile_raw = run_cmd([str(VENV_PY), "-m", "py_compile", str(raw_path)])
        compile_wrap = run_cmd([str(VENV_PY), "-m", "py_compile", str(wrap_path)])
        as_published_run = run_cmd(
            [str(VENV_PY), str(raw_path)],
            env={"CALLE_API_KEY": "iams_lab_fake", "CALLE_BASE_URL": "http://127.0.0.1:1"},
            timeout=8,
        )
        as_published_text = as_published_run["stdout"] + "\n" + as_published_run["stderr"]
        as_published_name_error = bool(
            re.search(r"NameError|AttributeError|ImportError|SyntaxError", as_published_text)
        )
        type_cmd = None
        if mypy.exists():
            type_cmd = run_cmd(
                [str(mypy), "--pretty", "--no-error-summary", str(wrap_path)],
                env={"MYPYPATH": str(LAB / "venv" / "lib" / "python3.12" / "site-packages")},
            )
        elif pyright:
            type_cmd = run_cmd([pyright, str(wrap_path)])
        runtime = None
        if kind in {"complete", "continuation"}:
            runtime = run_cmd(
                [str(VENV_PY), str(wrap_path)],
                env={
                    "CALLE_API_KEY": "iams_lab_fake",
                    "CALLE_BASE_URL": "http://127.0.0.1:1",
                },
                timeout=8,
            )
        type_errors = []
        if type_cmd:
            type_errors = [
                line
                for line in (type_cmd["stdout"] + "\n" + type_cmd["stderr"]).splitlines()
                if line.strip()
                and "error:" in line.lower()
                and str(wrap_path) in line
            ][:12]
        runtime_err = ""
        runtime_ok = True
        if runtime:
            combined = runtime["stdout"] + "\n" + runtime["stderr"]
            runtime_ok = not re.search(
                r"AttributeError|NameError|TypeError|ImportError",
                combined,
            )
            runtime_err = combined[-1500:]
            # Connection errors against 127.0.0.1:1 are expected and count as pass.
            if "CalleConnectionError" in combined or "ConnectError" in combined or "Connection" in combined:
                runtime_ok = True
        rows.append(
            {
                "id": sample["id"],
                "source": sample["source"],
                "start_line": sample["start_line"],
                "lang": "python",
                "kind": kind,
                "pass": compile_raw["returncode"] == 0
                and compile_wrap["returncode"] == 0
                and runtime_ok
                and not (kind in {"complete", "handler_fragment"} and as_published_name_error),
                "as_published_name_error": as_published_name_error,
                "as_published_excerpt": as_published_text[-500:],
                "py_compile_raw": compile_raw["returncode"] == 0,
                "py_compile_wrap": compile_wrap["returncode"] == 0,
                "type_errors": type_errors,
                "runtime_ok": runtime_ok,
                "runtime_excerpt": runtime_err[-800:] if runtime_err else "",
                "raw_syntax_err": compile_raw["stderr"][-400:] if compile_raw["returncode"] else "",
            }
        )
    (OUT / "py-work-dir.txt").write_text(str(work), encoding="utf-8")
    return rows


def parse_curl(body: str) -> dict | None:
    if "curl" not in body:
        return None
    method = "POST" if re.search(r"-X\s+POST|--request POST", body) else "GET"
    url_match = re.search(r"https://api\.heycall-e\.com[^\"'\s]+|\$CALLE_BASE_URL[^\"'\s]*", body)
    url = url_match.group(0) if url_match else ""
    headers = re.findall(r"--header|-H\s+\"([^\"]+)\"|-H\s+'([^']+)'", body)
    header_vals = [a or b for a, b in headers]
    # also --header "..."
    header_vals += re.findall(r"--header \"([^\"]+)\"", body)
    data_match = re.search(r"--data '(\{.*\})'|--data \"(\{.*\})\"|-d '(\{.*\})'", body, re.DOTALL)
    raw_json = ""
    if data_match:
        raw_json = next(g for g in data_match.groups() if g)
    parsed = None
    json_error = None
    if raw_json:
        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            json_error = str(exc)
    return {
        "method": method,
        "url": url,
        "headers": sorted(set(header_vals)),
        "json": parsed,
        "json_error": json_error,
        "has_auth": any("Authorization" in h for h in header_vals) or "Authorization" in body,
        "has_content_type": any("Content-Type" in h for h in header_vals) or "Content-Type" in body,
        "has_idempotency": "Idempotency-Key" in body,
    }


def load_openapi_paths() -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        return {}
    spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
    return spec.get("paths", {})


def normalize_path(url: str) -> str:
    path = url
    path = path.replace("https://api.heycall-e.com", "")
    path = path.replace("$CALLE_BASE_URL", "")
    path = path.replace("${CALLE_GOAL_ID}", "{goal_id}")
    path = path.replace("$CALLE_GOAL_ID", "{goal_id}")
    path = path.replace("$CALLE_CALL_ID", "{call_id}")
    path = path.replace("${GOAL_RUN_ID}", "{goal_run_id}")
    path = re.sub(r"\?.*", "", path)
    return path or "/"


def check_curl(samples: list[dict]) -> list[dict]:
    paths = load_openapi_paths()
    create_props = {
        "task",
        "recipients",
        "recipient",
        "result_schema",
        "recipient_result_schema",
        "metadata",
        "webhook_url",
    }
    rows = []
    for sample in samples:
        if sample["lang"] != "bash" or "curl" not in sample["body"]:
            continue
        parsed = parse_curl(sample["body"])
        if not parsed:
            continue
        path = normalize_path(parsed["url"])
        # Map documented paths onto OpenAPI templates
        spec_path = None
        for candidate in paths:
            template = candidate
            if path == candidate or path.split("?")[0] == candidate:
                spec_path = candidate
                break
            # wildcard
            rx = re.sub(r"\{[^}]+\}", r"[^/]+", template)
            if re.fullmatch(rx, path.split("?")[0] or path):
                spec_path = candidate
                break
        issues = []
        if parsed["json_error"]:
            issues.append(f"invalid JSON: {parsed['json_error']}")
        if not parsed["has_auth"]:
            issues.append("missing Authorization header")
        if parsed["method"] == "POST" and not parsed["has_content_type"]:
            issues.append("POST missing Content-Type")
        if spec_path is None:
            issues.append(f"path not in OpenAPI: {path}")
        if parsed["json"] and spec_path == "/v1/calls":
            extra = set(parsed["json"]) - create_props
            if extra:
                issues.append(f"fields not in CreateCallRequest: {sorted(extra)}")
            if "task" not in parsed["json"]:
                issues.append("CreateCallRequest missing required task")
        if spec_path and spec_path.endswith("/runs") and parsed["json"]:
            if "phone" not in parsed["json"]:
                issues.append("Goal Run create missing required phone")
            extra = set(parsed["json"]) - {"phone", "variables"}
            if extra:
                issues.append(f"Goal Run extra fields: {sorted(extra)}")
        rows.append(
            {
                "id": sample["id"],
                "source": sample["source"],
                "start_line": sample["start_line"],
                "lang": "bash-curl",
                "kind": "complete",
                "method": parsed["method"],
                "path": path,
                "spec_path": spec_path,
                "pass": not issues,
                "issues": issues,
                "headers": parsed["headers"],
            }
        )
    return rows


def extract_cli_argvs() -> list[dict]:
    roots = [
        LAB / "call-e-integrations" / "skills",
        LAB / "call-e-integrations" / "docs" / "mcp",
        LAB / "call-e-integrations" / "docs" / "install",
        LAB / "call-e-integrations" / "packages" / "cli" / "docs",
    ]
    argvs = []
    array_re = re.compile(r"```json\n(\[[\s\S]*?\])\n```")
    calle_re = re.compile(r"`calle ([^`]+)`")
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            rel = str(path.relative_to(LAB / "call-e-integrations"))
            for index, match in enumerate(array_re.finditer(text), start=1):
                try:
                    arr = json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
                if isinstance(arr, list) and arr and isinstance(arr[0], str):
                    argvs.append({"source": rel, "index": index, "argv": arr, "kind": "json_argv"})
            for index, match in enumerate(calle_re.finditer(text), start=1):
                argvs.append(
                    {
                        "source": rel,
                        "index": index,
                        "argv": match.group(1).split(),
                        "kind": "inline_calle",
                    }
                )
    return argvs


def check_cli() -> list[dict]:
    if not CALLE.exists():
        return [{"id": "cli", "pass": False, "issues": ["calle binary missing"]}]
    help_cache: dict[str, str] = {}

    def help_text(parts: list[str]) -> str:
        key = " ".join(parts)
        if key not in help_cache:
            result = run_cmd([str(CALLE), *parts, "--help"])
            help_cache[key] = result["stdout"] + "\n" + result["stderr"]
        return help_cache[key]

    rows = []
    # Documented flags that must exist
    probes = [
        (["call", "plan"], ["--to-phone", "--goal", "--language", "--region", "--json"], ["--phone"]),
        (["call", "start"], ["--to-phone", "--goal", "--json"], ["--phone"]),
        (["call", "status"], ["--run-id", "--cursor", "--limit", "--json"], ["--phone"]),
        (["call", "run"], ["--plan-id", "--confirm-token"], []),
        (["call", "recover"], ["--recovery-id"], []),
        (["auth", "login"], ["--start-only", "--no-browser-open", "--json"], []),
        (["auth", "status"], ["--json"], []),
        (["mcp", "tools"], ["--json"], []),
        (["mcp", "call"], ["--args-json"], []),
        ([], ["--json", "--help"], []),
    ]
    for cmd, required, forbidden in probes:
        text = help_text(cmd)
        missing = [flag for flag in required if flag not in text]
        present_forbidden = [flag for flag in forbidden if re.search(rf"{re.escape(flag)}\b", text)]
        rows.append(
            {
                "id": f"help:{' '.join(cmd) or 'root'}",
                "source": "cli --help",
                "lang": "cli",
                "kind": "help",
                "pass": not missing and not present_forbidden,
                "missing": missing,
                "forbidden_present": present_forbidden,
                "excerpt": text[:400],
            }
        )

    # Unknown --phone must fail on call plan (offline, no network needed for help/unknown option)
    phone_probe = run_cmd(
        [str(CALLE), "call", "plan", "--phone", "+15551234567", "--goal", "lab", "--help"],
        env={"CALLE_CACHE_ROOT": str(LAB / "lab-out" / "empty-cache")},
    )
    # --help wins; also try without --help expecting unknown option. Do not place a call.
    unknown = run_cmd(
        [str(CALLE), "call", "plan", "--phone", "+15551234567", "--goal", "lab", "--timeout-seconds", "1"],
        env={
            "CALLE_CACHE_ROOT": str(LAB / "lab-out" / "empty-cache"),
            "CALLE_BASE_URL": "http://127.0.0.1:1",
        },
        timeout=8,
    )
    unknown_text = unknown["stdout"] + unknown["stderr"]
    rows.append(
        {
            "id": "cli:unknown-phone-flag",
            "source": "calle call plan --phone",
            "lang": "cli",
            "kind": "offline_flag",
            "pass": "Unknown option" in unknown_text or "unknown option" in unknown_text.lower() or unknown["returncode"] != 0,
            "excerpt": unknown_text[-600:],
            "returncode": unknown["returncode"],
        }
    )

    argvs = extract_cli_argvs()
    for item in argvs:
        argv = item["argv"]
        if argv[:1] == ["npx"] or "run-agent-command" in " ".join(argv):
            continue
        if argv in (["--help"], ["--version"], ["-h"], ["-V"]):
            result = run_cmd([str(CALLE), *argv])
            rows.append(
                {
                    "id": f"{item['source']}:{item['index']}",
                    "source": item["source"],
                    "lang": "cli",
                    "kind": item["kind"],
                    "argv": argv,
                    "pass": result["returncode"] == 0,
                    "excerpt": (result["stdout"] + result["stderr"])[:300],
                }
            )
            continue
        # Validate flags against help only; never run plan/start/run against a server.
        if argv[0] in {"call", "auth", "mcp", "regions"}:
            help_parts = argv[:2] if len(argv) >= 2 and not argv[1].startswith("-") else argv[:1]
            text = help_text(help_parts if help_parts != ["call"] else argv[:2])
            flags = [tok for tok in argv if tok.startswith("--")]
            missing = [
                flag
                for flag in flags
                if flag.split("=", 1)[0] not in text and flag not in {"--args-json"}
            ]
            # --args-json is on mcp call
            if "--args-json" in flags:
                mcp_help = help_text(["mcp", "call"])
                if "--args-json" not in mcp_help:
                    missing.append("--args-json")
                missing = [m for m in missing if m != "--args-json"]
            rows.append(
                {
                    "id": f"{item['source']}:{item['kind']}:{item['index']}",
                    "source": item["source"],
                    "lang": "cli",
                    "kind": item["kind"],
                    "argv": argv,
                    "pass": not missing,
                    "missing": missing,
                }
            )
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    samples = load_fences()
    ts_rows = check_typescript(samples)
    py_rows = check_python(samples)
    curl_rows = check_curl(samples)
    cli_rows = check_cli()
    report = {
        "typescript": ts_rows,
        "python": py_rows,
        "curl": curl_rows,
        "cli": cli_rows,
    }
    (OUT / "sample-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    def summarize(name: str, rows: list[dict]) -> None:
        passed = sum(1 for r in rows if r.get("pass"))
        print(f"{name}: {passed}/{len(rows)} pass")
        for row in rows:
            if not row.get("pass"):
                print(f"  FAIL {row.get('id')} {row.get('issues') or row.get('errors') or row.get('missing') or row.get('type_errors')}")

    summarize("typescript", ts_rows)
    summarize("python", py_rows)
    summarize("curl", curl_rows)
    summarize("cli", cli_rows)


if __name__ == "__main__":
    main()
