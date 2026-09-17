#!/usr/bin/env python3
"""Minimal webhook sink: logs every request (headers + body) to a private jsonl."""
import datetime as dt
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

OUT = Path(__file__).resolve().parents[4] / ".data" / "live-2026-09-17" / "webhooks.jsonl"
OUT.parent.mkdir(parents=True, exist_ok=True)


class H(BaseHTTPRequestHandler):
    def _log(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""
        try:
            parsed = json.loads(body)
        except ValueError:
            parsed = None
        rec = {"t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"), "method": self.command,
               "path": self.path, "headers": dict(self.headers), "json": parsed, "raw": None if parsed is not None else body[:1000].decode("utf-8", "replace")}
        with OUT.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        summ = {"t": rec["t"], "method": self.command, "path": self.path, "type": (parsed or {}).get("type"),
                "status": ((parsed or {}).get("data") or {}).get("status"), "id": (parsed or {}).get("id"),
                "sig_headers": [k for k in self.headers.keys() if "sig" in k.lower() or "hmac" in k.lower() or k.lower().startswith("x-calle") or k.lower().startswith("calle")]}
        print(json.dumps(summ), flush=True)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    do_POST = _log
    do_GET = _log
    do_PUT = _log

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    print("listening", port, "->", OUT, flush=True)
    HTTPServer(("127.0.0.1", port), H).serve_forever()
