#!/usr/bin/env python3
"""Live Calls API runner for the 2026-09-17 feedback lab.

Raw responses (which contain the recipient number and transcript) go to
.data/live-2026-09-17/<case>/ and are never committed. Everything printed
here is redacted (phone numbers replaced) so it can be pasted into LIVE_LOG.md.

Usage:
  live.py create <case> --task FILE --schema FILE [--idem KEY] [--webhook URL] [--meta k=v]
  live.py get <case> <call_id>
  live.py poll <case> <call_id> [--every 5] [--max 900]
  live.py events <case> <call_id>
  live.py raw <case> <call_id>          # dump full redacted object
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[4]
PRIVATE = ROOT / ".data" / "live-2026-09-17"
ENV = Path("/Users/arshdeepsingh/Developer/CallE/.env.local")
BASE = "https://api.heycall-e.com"
PHONE_RE = re.compile(r"\+?91\s?\d{5}\s?\d{5}|\+\d{9,15}")


def env():
    values = {}
    for line in ENV.read_text().splitlines():
        line = line.strip().removeprefix("export ")
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip().strip("\"'")
    phone = re.sub(r"[ ()-]", "", values["CALLE_TEST_PHONE"])
    return values["CALLE_API_KEY"], phone


def redact(obj):
    s = json.dumps(obj, indent=1, ensure_ascii=False)
    return PHONE_RE.sub("<phone>", s)


def token_note(v):
    """Describe a token field without ever reporting null as a credential."""
    if v is None:
        return "null (no token)"
    if isinstance(v, str):
        return f"present (<{len(v)} chars>)"
    return f"present ({type(v).__name__})"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def save(case, name, payload):
    d = PRIVATE / case
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    p.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    os.chmod(p, 0o600)
    return p


def call(method, path, key, **kw):
    t0 = time.monotonic()
    r = requests.request(method, BASE + path, headers={"Authorization": f"Bearer {key}", **kw.pop("headers", {})}, timeout=30, **kw)
    ms = round((time.monotonic() - t0) * 1000)
    try:
        body = r.json()
    except ValueError:
        body = {"_non_json_body": r.text[:500]}
    return r.status_code, dict(r.headers), body, ms


def brief(d):
    recs = d.get("recipients") or []
    atts = [a for r in recs for a in (r.get("attempts") or [])]
    return {
        "t": now(),
        "status": d.get("status"),
        "recipient_status": [r.get("status") for r in recs],
        "attempt_status": [a.get("status") for a in atts],
        "attempt_started_at": [a.get("started_at") for a in atts],
        "turns": [len(a.get("transcript_turns") or []) for a in atts],
        "failure_code": d.get("failure_code"),
        "task_completed": d.get("task_completed"),
        "has_structured_result": d.get("structured_result") is not None,
        "completed_at": d.get("completed_at"),
    }


def cmd_create(a):
    key, phone = env()
    task = Path(a.task).read_text().strip()
    body = {"task": task, "recipients": [{"phones": [phone]}]}
    if a.schema:
        body["result_schema"] = json.loads(Path(a.schema).read_text())
    if a.webhook:
        body["webhook_url"] = a.webhook
    meta = {"lab": "feedback-2026-09-17", "case": a.case}
    for kv in a.meta or []:
        k, v = kv.split("=", 1)
        meta[k] = v
    body["metadata"] = meta
    headers = {"Content-Type": "application/json"}
    if a.idem:
        headers["Idempotency-Key"] = a.idem
    save(a.case, f"request-{int(time.time())}.json", {"headers": {k: v for k, v in headers.items()}, "body": body})
    status, hdrs, resp, ms = call("POST", "/v1/calls", key, headers=headers, data=json.dumps(body))
    save(a.case, f"created-{int(time.time())}.json", {"status": status, "headers": hdrs, "body": resp})
    print(json.dumps({"t": now(), "http": status, "ms": ms, "id": resp.get("id"), "status": resp.get("status"),
                      "error": resp.get("error"), "req_headers": {k: hdrs.get(k) for k in ("x-request-id", "retry-after", "idempotency-key", "idempotent-replayed") if hdrs.get(k)}}))
    if status >= 400:
        print(redact(resp))


def cmd_get(a):
    key, _ = env()
    status, hdrs, d, ms = call("GET", f"/v1/calls/{a.call_id}", key)
    save(a.case, f"get-{int(time.time()*1000)}.json", d)
    print(json.dumps({**brief(d), "http": status, "ms": ms}))


def cmd_poll(a):
    key, _ = env()
    t0 = time.monotonic()
    last = None
    log = PRIVATE / a.case / "polls.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    while time.monotonic() - t0 < a.max:
        status, hdrs, d, ms = call("GET", f"/v1/calls/{a.call_id}", key)
        b = {**brief(d), "http": status, "ms": ms, "elapsed": round(time.monotonic() - t0, 1)}
        with log.open("a") as f:
            f.write(json.dumps({"t": now(), "elapsed": b["elapsed"], "body": d}) + "\n")
        sig = json.dumps({k: b[k] for k in ("status", "recipient_status", "attempt_status", "turns", "failure_code", "has_structured_result")})
        if sig != last:
            print(json.dumps(b), flush=True)
            last = sig
        if d.get("status") in ("completed", "failed", "canceled"):
            save(a.case, "terminal.json", d)
            print("TERMINAL after", b["elapsed"], "s")
            return
        time.sleep(a.every)
    print("LOCAL DEADLINE reached; call may still be live. Not redialing.")


def cmd_events(a):
    key, _ = env()
    cursor = None
    page = 0
    allrows = []
    while True:
        q = f"?cursor={cursor}" if cursor else ""
        status, hdrs, d, ms = call("GET", f"/v1/calls/{a.call_id}/events{q}", key)
        rows = d.get("data") or []
        allrows += rows
        print(f"page {page}: http {status} rows {len(rows)} next_cursor {d.get('next_cursor')!r}")
        for e in rows:
            print(" ", e.get("created_at"), e.get("type"), "| status:", e.get("status"), "|", e.get("level"), e.get("message"))
        page += 1
        cursor = d.get("next_cursor")
        if not cursor or not rows:
            break
    save(a.case, f"events-{int(time.time())}.json", allrows)


def cmd_raw(a):
    key, _ = env()
    status, hdrs, d, ms = call("GET", f"/v1/calls/{a.call_id}", key)
    save(a.case, f"raw-{int(time.time())}.json", d)
    d.pop("task", None)
    print(redact(d))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create"); c.add_argument("case"); c.add_argument("--task", required=True); c.add_argument("--schema"); c.add_argument("--idem"); c.add_argument("--webhook"); c.add_argument("--meta", action="append"); c.set_defaults(fn=cmd_create)
    for name, fn in (("get", cmd_get), ("events", cmd_events), ("raw", cmd_raw)):
        s = sub.add_parser(name); s.add_argument("case"); s.add_argument("call_id"); s.set_defaults(fn=fn)
    s = sub.add_parser("poll"); s.add_argument("case"); s.add_argument("call_id"); s.add_argument("--every", type=float, default=5); s.add_argument("--max", type=float, default=900); s.set_defaults(fn=cmd_poll)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
