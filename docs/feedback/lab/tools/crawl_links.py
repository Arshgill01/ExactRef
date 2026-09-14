#!/usr/bin/env python3
"""Crawl docs.heycall-e.com plus README/package/Devpost links. Read-only HTTP.

Does not submit forms, post to Discord/GitHub, or call the Calls API.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

LAB = Path("/tmp/calle-lab")
OUT = LAB / "lab-out"
DOCS = "https://docs.heycall-e.com"
UA = "ExactRef-feedback-lab/0.1 (+offline docs audit; no form submit)"
TIMEOUT = 20
SKIP_PREFIXES = (
    "mailto:",
    "javascript:",
    "data:",
)
# Do not join Discord or open issue/PR flows. HEAD/GET public pages only.
DISCORD_HOSTS = {"discord.gg", "discord.com", "discordapp.com"}

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
HREF_RE = re.compile(r"""href=["']([^"']+)["']""", re.I)
SRC_RE = re.compile(r"""(?:src|content)=["'](https?://[^"']+)["']""", re.I)
MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.M)
HTML_ID_RE = re.compile(r"""\sid=["']([^"']+)["']""", re.I)
SITEMAP_LOC_RE = re.compile(r"<loc>([^<]+)</loc>", re.I)


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.title = ""
        self.og_title = ""
        self.og_desc = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k: v or "" for k, v in attrs}
        if "id" in ad:
            self.ids.add(ad["id"])
        if tag == "title":
            self._in_title = True
        if tag == "meta" and ad.get("property") == "og:title":
            self.og_title = ad.get("content", "")
        if tag == "meta" and ad.get("property") == "og:description":
            self.og_desc = ad.get("content", "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def fetch(url: str, method: str = "GET") -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return {"url": url, "status": None, "error": "unsupported scheme", "final": url, "body": "", "headers": {}}
    # curl uses the macOS/system CA bundle. Python's urllib on this host
    # fails with CERTIFICATE_VERIFY_FAILED against docs.heycall-e.com.
    tmp = tempfile.NamedTemporaryFile(prefix="calle-crawl-", delete=False)
    body_path = Path(tmp.name)
    tmp.close()
    cmd = [
        "curl",
        "-sS",
        "-L",
        "--max-redirs",
        "8",
        "--max-time",
        str(TIMEOUT),
        "-A",
        UA,
        "-D",
        str(body_path) + ".hdr",
        "-o",
        str(body_path),
        "-w",
        "%{http_code}\n%{url_effective}\n%{content_type}\n",
        "-X",
        method,
        url,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT + 5)
    except subprocess.TimeoutExpired:
        return {"url": url, "status": None, "error": "timeout", "final": url, "body": "", "headers": {}, "content_type": ""}
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    status = None
    final = url
    content_type = ""
    if len(lines) >= 1 and lines[0].isdigit():
        status = int(lines[0])
    if len(lines) >= 2:
        final = lines[1]
    if len(lines) >= 3:
        content_type = lines[2]
    try:
        body = body_path.read_text(encoding="utf-8", errors="replace")[:400_000]
    except OSError:
        body = ""
    headers: dict[str, str] = {}
    try:
        hdr = body_path.with_suffix(".hdr").read_text(encoding="utf-8", errors="replace")
        for block in hdr.split("\r\n\r\n"):
            for line in block.splitlines():
                if ":" in line and not line.startswith("HTTP/"):
                    k, v = line.split(":", 1)
                    headers[k.strip().lower()] = v.strip()
    except OSError:
        pass
    body_path.unlink(missing_ok=True)
    body_path.with_suffix(".hdr").unlink(missing_ok=True)
    if proc.returncode != 0 and status is None:
        return {
            "url": url,
            "status": None,
            "error": proc.stderr.strip() or f"curl exit {proc.returncode}",
            "final": final,
            "body": body,
            "headers": headers,
            "content_type": content_type or headers.get("content-type", ""),
        }
    return {
        "url": url,
        "status": status,
        "final": final,
        "error": None if status and status < 400 else (proc.stderr.strip() or None),
        "body": body,
        "headers": headers,
        "content_type": content_type or headers.get("content-type", ""),
    }


def slugify_heading(text: str) -> str:
    text = re.sub(r"`+", "", text).strip().lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def extract_md_ids(text: str) -> set[str]:
    ids = set(re.findall(r'<a id="([^"]+)"', text))
    for match in MD_HEADING_RE.finditer(text):
        ids.add(slugify_heading(match.group(2)))
    return ids


def extract_links(text: str, base: str) -> list[str]:
    found = []
    for match in LINK_RE.finditer(text):
        found.append(match.group(2).strip())
    for match in HREF_RE.finditer(text):
        found.append(match.group(1).strip())
    out = []
    for raw in found:
        href = raw.split()[0].strip("<>")
        if not href or href.startswith(SKIP_PREFIXES):
            continue
        out.append(urljoin(base, href))
    return out


def is_docs(url: str) -> bool:
    return urlparse(url).netloc == "docs.heycall-e.com"


def classify_status(probe: dict) -> str:
    status = probe.get("status")
    final = probe.get("final") or ""
    if status is None:
        return "error"
    if status == 404:
        return "404"
    if status >= 400:
        return f"http_{status}"
    if "404" in (probe.get("final") or "") and status == 200:
        return "redirect_to_404"
    if urlparse(probe.get("url", "")).scheme == "http" and urlparse(final).scheme == "https":
        return "ok_http_redirect"
    if urlparse(probe.get("url", "")).scheme == "http":
        return "mixed_http"
    return "ok"


def crawl_docs() -> dict:
    robots = fetch(f"{DOCS}/robots.txt")
    sitemap = fetch(f"{DOCS}/sitemap.xml")
    llms = fetch(f"{DOCS}/llms.txt")
    llms_full = fetch(f"{DOCS}/llms-full.txt")
    locs = SITEMAP_LOC_RE.findall(sitemap.get("body") or "")
    # also seed from llms.txt
    llms_paths = re.findall(r"\((/[^)]+)\)", llms.get("body") or "")
    seeds = list(dict.fromkeys(locs + [urljoin(DOCS, p) for p in llms_paths] + [
        f"{DOCS}/",
        f"{DOCS}/quickstart",
        f"{DOCS}/mcp",
        f"{DOCS}/mcp.md",
        f"{DOCS}/api-reference",
        f"{DOCS}/api-reference.md",
        f"{DOCS}/regions",
        f"{DOCS}/regions.md",
        f"{DOCS}/openapi/calle.openapi.yaml",
        f"{DOCS}/llms.txt",
        f"{DOCS}/llms-full.txt",
        f"{DOCS}/sitemap.xml",
        f"{DOCS}/robots.txt",
        f"{DOCS}/favicon.svg",
        f"{DOCS}/pagefind/pagefind-entry.json",
        f"{DOCS}/pagefind/pagefind.js",
    ]))

    pages: dict[str, dict] = {}
    internal_targets: set[str] = set()
    fragment_checks: list[dict] = []
    broken: list[dict] = []
    all_external: set[str] = set()

    queue = list(seeds)
    seen: set[str] = set()
    while queue:
        url = queue.pop(0)
        url_nf, _frag = urldefrag(url)
        if url_nf in seen:
            continue
        seen.add(url_nf)
        if not is_docs(url_nf) and url_nf not in seeds:
            continue
        time.sleep(0.05)
        probe = fetch(url_nf)
        kind = classify_status(probe)
        parser = IdCollector()
        try:
            parser.feed(probe.get("body") or "")
        except Exception:
            pass
        pages[url_nf] = {
            "status": probe.get("status"),
            "final": probe.get("final"),
            "kind": kind,
            "title": parser.title.strip(),
            "og_title": parser.og_title,
            "og_desc": parser.og_desc,
            "content_type": probe.get("content_type"),
            "ids_count": len(parser.ids),
            "error": probe.get("error"),
        }
        if kind not in {"ok", "ok_http_redirect"}:
            broken.append({"url": url_nf, "kind": kind, "status": probe.get("status"), "final": probe.get("final"), "error": probe.get("error")})

        body = probe.get("body") or ""
        for link in extract_links(body, url_nf):
            link_nf, frag = urldefrag(link)
            parsed = urlparse(link_nf)
            if parsed.netloc == "docs.heycall-e.com" or (not parsed.netloc and parsed.path.startswith("/")):
                abs_link = link_nf if parsed.netloc else urljoin(DOCS, parsed.path)
                internal_targets.add(abs_link)
                if abs_link not in seen and abs_link not in queue:
                    queue.append(abs_link)
                if frag:
                    fragment_checks.append({"page": url_nf, "href": link, "target": abs_link, "frag": frag})
            else:
                if parsed.scheme in {"http", "https"}:
                    all_external.add(link_nf)

        # markdown heading ids for .md pages
        if url_nf.endswith(".md"):
            pages[url_nf]["md_ids"] = sorted(extract_md_ids(body))[:50]

        # store ids for fragment resolution
        pages[url_nf]["ids"] = sorted(parser.ids)[:400]

    # resolve fragments
    bad_frags = []
    for item in fragment_checks:
        target = pages.get(item["target"])
        if not target:
            bad_frags.append({**item, "reason": "target page not crawled"})
            continue
        ids = set(target.get("ids") or [])
        if item["frag"] not in ids:
            # zudoku may slug differently
            bad_frags.append({**item, "reason": "heading id missing", "available_sample": sorted(ids)[:20]})

    return {
        "robots": {"status": robots.get("status"), "body": robots.get("body")},
        "sitemap_locs": locs,
        "llms": {"status": llms.get("status"), "body": llms.get("body")},
        "llms_full_status": llms_full.get("status"),
        "llms_full_len": len(llms_full.get("body") or ""),
        "pages": {k: {kk: vv for kk, vv in v.items() if kk != "ids"} | {"ids": v.get("ids", [])} for k, v in pages.items()},
        "broken_internal": broken,
        "bad_fragments": bad_frags,
        "external_urls": sorted(all_external),
        "internal_count": len(pages),
    }


def extra_markdown_sources() -> list[tuple[str, Path]]:
    roots = [
        LAB / "call-e-integrations",
        LAB / "server-sdk-typescript",
        LAB / "server-sdk-python",
    ]
    files = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            if any(p in {".git", "node_modules", "dist"} for p in path.parts):
                continue
            rel = str(path.relative_to(root))
            if rel in {
                "README.md",
                "SECURITY.md",
                "CONTRIBUTING.md",
                "docs/mcp/openagent-oauth.md",
                "docs/install/install-guide.md",
                "docs/install/CALL-E-installation-guide.md",
                "docs/install/cli.md",
                "skills/calle/SKILL.md",
                "skills/calle/references/commands.md",
            } or rel.endswith("SKILL.md") or rel.endswith("commands.md") or rel.startswith("docs/install/"):
                files.append((f"{root.name}:{rel}", path))
    return files


def crawl_markdown_and_packages(external_from_docs: list[str]) -> dict:
    extras = [
        "https://www.npmjs.com/package/@call-e/calle",
        "https://www.npmjs.com/package/@call-e/cli",
        "https://pypi.org/pypi/calle-ai/json",
        "https://pypi.org/project/calle-ai/",
        "https://call-e.devpost.com/",
        "https://call-e.devpost.com/rules",
        "https://call-e.devpost.com/resources",
        "https://call-e.devpost.com/details/resources",
        "https://call-e.devpost.com/details/dates",
        "https://github.com/CALLE-AI/server-sdk-typescript",
        "https://github.com/CALLE-AI/server-sdk-python",
        "https://github.com/CALLE-AI/call-e-integrations",
        "https://github.com/CALLE-AI/calle-docs",
        "https://open.heycall-e.com/document/mcp-archive/CALL-E-installation-guide.md",
        "https://dashboard.heycall-e.com/",
        "https://dashboard.heycall-e.com/account/api-keys",
        "https://www.heycall-e.com/",
        "https://clawhub.ai/call-e-dev/phone-call-calle",
        "https://modelcontextprotocol.io/docs/tools/inspector",
    ]
    md_links: list[tuple[str, str]] = []
    for label, path in extra_markdown_sources():
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            href = match.group(2).strip().split()[0]
            if href.startswith(("http://", "https://")):
                md_links.append((f"{label}", href))
    # package.json homepage/bugs
    for pkg in [
        LAB / "tslab" / "node_modules" / "@call-e" / "calle" / "package.json",
        LAB / "tslab" / "node_modules" / "@call-e" / "cli" / "package.json",
    ]:
        if pkg.exists():
            data = json.loads(pkg.read_text(encoding="utf-8"))
            for key in ("homepage",):
                if data.get(key):
                    extras.append(data[key])
            if isinstance(data.get("bugs"), dict) and data["bugs"].get("url"):
                extras.append(data["bugs"]["url"])
            if isinstance(data.get("repository"), dict) and data["repository"].get("url"):
                extras.append(data["repository"]["url"].replace("git+", "").replace(".git", ""))

    to_probe = []
    for url in extras + external_from_docs + [u for _, u in md_links]:
        nf, _ = urldefrag(url)
        if urlparse(nf).scheme in {"http", "https"}:
            to_probe.append(nf)
    # unique
    to_probe = list(dict.fromkeys(to_probe))

    results = []
    broken = []
    for url in to_probe:
        host = urlparse(url).netloc
        # Discord: record URL only; GET invite page is read-only and does not join.
        time.sleep(0.08)
        probe = fetch(url)
        kind = classify_status(probe)
        row = {
            "url": url,
            "status": probe.get("status"),
            "final": probe.get("final"),
            "kind": kind,
            "error": probe.get("error"),
            "discord": host in DISCORD_HOSTS,
        }
        results.append(row)
        if kind not in {"ok", "ok_http_redirect"}:
            broken.append(row)
    return {
        "probes": results,
        "broken": broken,
        "markdown_link_count": len(md_links),
    }


def check_md_variants(docs_pages: dict) -> list[dict]:
    rows = []
    for url, info in docs_pages.items():
        if not url.startswith(f"{DOCS}/"):
            continue
        path = urlparse(url).path
        if path in {"/sitemap.xml", "/robots.txt", "/llms.txt", "/llms-full.txt", "/favicon.svg"}:
            continue
        if path.startswith("/openapi/") or path.startswith("/pagefind/"):
            continue
        if path.endswith(".md") or path.endswith(".txt") or path.endswith(".xml") or path.endswith(".svg") or path.endswith(".js") or path.endswith(".json"):
            continue
        if info.get("status") != 200:
            continue
        md_url = url.rstrip("/") + ".md"
        # already crawled?
        existing = docs_pages.get(md_url)
        if existing:
            rows.append({"html": url, "md": md_url, "status": existing.get("status"), "pass": existing.get("status") == 200})
        else:
            probe = fetch(md_url)
            rows.append({"html": url, "md": md_url, "status": probe.get("status"), "pass": probe.get("status") == 200})
    return rows


def extract_package_page_urls(npm_html: str) -> list[str]:
    return sorted(set(re.findall(r"https://(?:github\.com|docs\.heycall-e\.com|www\.npmjs\.com)[^\"'\s<>]+", npm_html)))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    docs = crawl_docs()
    extras = crawl_markdown_and_packages(docs.get("external_urls") or [])
    md_variants = check_md_variants(docs["pages"])

    # pagefind / search
    pagefind = fetch(f"{DOCS}/pagefind/pagefind-entry.json")
    pagefind_js = fetch(f"{DOCS}/pagefind/pagefind.js")
    search_mcp = {
        "pagefind_entry_status": pagefind.get("status"),
        "pagefind_js_status": pagefind_js.get("status"),
        "pagefind_entry_excerpt": (pagefind.get("body") or "")[:1500],
        "mentions_mcp": "mcp" in (pagefind.get("body") or "").lower()
        or "plan_call" in (pagefind.get("body") or ""),
    }

    # npm/pypi listed urls
    npm_calle = next((p for p in extras["probes"] if p["url"].endswith("/package/@call-e/calle")), None)
    report = {
        "docs": {
            "robots": docs["robots"],
            "sitemap_locs": docs["sitemap_locs"],
            "llms": docs["llms"],
            "llms_full_status": docs["llms_full_status"],
            "llms_full_len": docs["llms_full_len"],
            "pages": {k: {kk: vv for kk, vv in v.items() if kk != "ids"} for k, v in docs["pages"].items()},
            "page_ids": {k: v.get("ids", []) for k, v in docs["pages"].items()},
            "broken_internal": docs["broken_internal"],
            "bad_fragments": docs["bad_fragments"],
            "internal_count": docs["internal_count"],
        },
        "external": extras,
        "md_variants": md_variants,
        "search": search_mcp,
        "npm_calle": npm_calle,
    }
    (OUT / "crawl-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"internal pages: {docs['internal_count']}")
    print(f"broken internal: {len(docs['broken_internal'])}")
    print(f"bad fragments: {len(docs['bad_fragments'])}")
    print(f"broken external: {len(extras['broken'])}")
    print(f"md variants: {sum(1 for r in md_variants if r['pass'])}/{len(md_variants)} have .md")
    for row in docs["broken_internal"]:
        print("  INT", row)
    for row in docs["bad_fragments"][:30]:
        print("  FRAG", row["href"], row.get("reason"))
    for row in extras["broken"]:
        print("  EXT", row["url"], row["status"], row.get("error"))


if __name__ == "__main__":
    main()
