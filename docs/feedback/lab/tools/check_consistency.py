#!/usr/bin/env python3
"""Version / default / placeholder / llms.txt consistency across the doc set."""

from __future__ import annotations

import json
import re
from pathlib import Path

LAB = Path("/tmp/calle-lab")
OUT = LAB / "lab-out"

VERSION_RE = re.compile(r"@call-e/(?:calle|cli)@?[0-9.]*|calle-ai==?[0-9.]*|0\.[0-9]+\.[0-9]+|API 0\.[0-9]")
TIMEOUT_RE = re.compile(
    r"timeout(?:Ms|_seconds)?\s*[:=]\s*[0-9_]+|interval(?:Ms|_seconds)?\s*[:=]\s*[0-9_]+|"
    r"timeout_seconds=\d+|poll every [^.\n]+|wait ~?\d+|120_000|600\.0|ttl_seconds|"
    r"Defaults to `\d+`|maximum `\d+`|limit=\d+|limit: \d+",
    re.I,
)
STATUS_RE = re.compile(
    r"`(?:queued|in_progress|completed|failed|canceled|cancelled|NO ANSWER|NO_ANSWER|"
    r"no_answer|BUSY|VOICEMAIL|EXPIRED|DECLINED)`"
)
PLACEHOLDER_RE = re.compile(
    r"Coming soon|TODO\b|TBD\b|<your-[a-z0-9_-]+>|FIXME|XXX\b|lorem ipsum",
    re.I,
)
E164_RE = re.compile(r"E\.164|\\+\[1-9\]|min(imum)? (length|7|8)|7,14|6,14|8,14")


def iter_text_files() -> list[tuple[str, str]]:
    files: list[tuple[str, str]] = []
    groups = [
        (LAB / "calle-docs" / "content" / "guides", "*.mdx"),
        (LAB / "calle-docs" / "examples", "*.py"),
        (LAB / "calle-docs" / "tests", "*.ts"),
        (LAB, "doc-*.md"),
        (LAB / "call-e-integrations" / "docs", "**/*.md"),
        (LAB / "call-e-integrations" / "skills", "**/*.md"),
        (LAB / "call-e-integrations", "README.md"),
        (LAB / "server-sdk-typescript", "README.md"),
        (LAB / "server-sdk-python", "README.md"),
        (LAB / "tslab" / "node_modules" / "@call-e" / "calle", "README.md"),
        (LAB / "tslab" / "node_modules" / "@call-e" / "cli", "README.md"),
    ]
    for root, pattern in groups:
        if not root.exists():
            continue
        for path in root.glob(pattern) if "*" in pattern or "?" in pattern else [root if root.is_file() else root / pattern]:
            if path.is_dir():
                continue
            if not path.exists() or not path.is_file():
                continue
            if any(p in {".git", "node_modules"} and "tslab" not in str(path) for p in path.parts):
                if "node_modules/@call-e" not in str(path):
                    if "node_modules" in path.parts and "@call-e" not in path.parts:
                        continue
            rel = str(path)
            files.append((rel, path.read_text(encoding="utf-8")))
    # fetched llms
    llms = LAB / "doc-llms.txt"
    if llms.exists():
        files.append((str(llms), llms.read_text(encoding="utf-8")))
    return files


def collect(pattern: re.Pattern[str], files: list[tuple[str, str]]) -> list[dict]:
    rows = []
    for rel, text in files:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            snippet = text[max(0, match.start() - 40) : match.end() + 40].replace("\n", " ")
            rows.append({"file": rel, "line": line, "match": match.group(0), "snippet": snippet.strip()})
    return rows


def playwright_pins() -> list[dict]:
    spec = (LAB / "calle-docs" / "tests" / "docs-site.spec.ts").read_text(encoding="utf-8")
    interesting = [
        r"Not currently public",
        r"@call-e/calle@0\.7\.0",
        r"calle-ai==0\.7\.0",
        r"/calle/webhook",
        r"pnpm add @call-e/calle",
        r"three tools",
        r"plan_call",
        r"Success fee",
        r"Indonesian",
        r"0\.5\.1",
        r"0\.7\.1",
        r"mcp",
    ]
    pins = []
    for rx in interesting:
        for match in re.finditer(rx, spec, re.I):
            line = spec.count("\n", 0, match.start()) + 1
            pins.append({"pattern": rx, "line": line, "match": match.group(0)})
    return pins


def compare_llms(crawl: dict) -> dict:
    llms_body = (crawl.get("docs") or {}).get("llms", {}).get("body") or ""
    sitemap = (crawl.get("docs") or {}).get("sitemap_locs") or []
    llms_paths = re.findall(r"\((/[^)]+)\)", llms_body)
    sitemap_paths = [u.replace("https://docs.heycall-e.com", "") or "/" for u in sitemap]
    missing_from_llms = sorted(
        p
        for p in sitemap_paths
        if p not in {"/"}
        and f"{p}.md" not in llms_paths
        and p not in llms_paths
        and not p.startswith("/api-reference/")
    )
    # API reference children are expected to be omitted if only the index is listed
    api_children = [p for p in sitemap_paths if p.startswith("/api-reference/")]
    listed_404 = []
    pages = (crawl.get("docs") or {}).get("pages") or {}
    for path in llms_paths:
        url = "https://docs.heycall-e.com" + path
        info = pages.get(url)
        if info and info.get("status") == 404:
            listed_404.append(path)
        elif path.endswith(".md"):
            html = "https://docs.heycall-e.com" + path[:-3]
            html_info = pages.get(html)
            if html_info and html_info.get("status") == 404:
                listed_404.append(path)
    descriptions = re.findall(r"- \[([^\]]+)\]\(([^)]+)\):\s*(.+)", llms_body)
    return {
        "llms_paths": llms_paths,
        "sitemap_paths": sitemap_paths,
        "sitemap_not_in_llms": missing_from_llms,
        "api_reference_children": api_children,
        "llms_listed_404": listed_404,
        "descriptions": [{"title": a, "path": b, "blurb": c} for a, b, c in descriptions],
        "mentions_mcp": "mcp" in llms_body.lower(),
        "mentions_cli": "cli" in llms_body.lower(),
        "mentions_skill": "skill" in llms_body.lower(),
    }


def main() -> None:
    files = iter_text_files()
    crawl = {}
    crawl_path = OUT / "crawl-report.json"
    if crawl_path.exists():
        crawl = json.loads(crawl_path.read_text(encoding="utf-8"))
    report = {
        "versions": collect(VERSION_RE, files),
        "timeouts": collect(TIMEOUT_RE, files),
        "statuses": collect(STATUS_RE, files),
        "placeholders": collect(PLACEHOLDER_RE, files),
        "e164": collect(E164_RE, files),
        "playwright_pins": playwright_pins(),
        "llms_vs_sitemap": compare_llms(crawl),
        "file_count": len(files),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "consistency-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"files: {len(files)}")
    print(f"version hits: {len(report['versions'])}")
    print(f"timeout hits: {len(report['timeouts'])}")
    print(f"status hits: {len(report['statuses'])}")
    print(f"placeholder hits: {len(report['placeholders'])}")
    print("placeholders:")
    for row in report["placeholders"]:
        print(f"  {row['file']}:{row['line']}: {row['match']}")
    print("playwright pins:")
    for row in report["playwright_pins"]:
        print(f"  L{row['line']}: {row['match']}")
    llms = report["llms_vs_sitemap"]
    print("llms missing sitemap pages:", llms.get("sitemap_not_in_llms"))
    print("llms 404:", llms.get("llms_listed_404"))
    print("llms mcp/cli/skill:", llms.get("mentions_mcp"), llms.get("mentions_cli"), llms.get("mentions_skill"))


if __name__ == "__main__":
    main()
