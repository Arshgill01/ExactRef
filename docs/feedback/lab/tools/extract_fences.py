#!/usr/bin/env python3
"""Extract fenced code blocks from CALL-E docs sources. No tokens, no network."""

from __future__ import annotations

import json
import re
from pathlib import Path

FENCE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)[^\n]*\n(.*?)```", re.DOTALL)

LANG_ALIASES = {
    "ts": "typescript",
    "tsx": "typescript",
    "js": "javascript",
    "javascript": "javascript",
    "typescript": "typescript",
    "py": "python",
    "python": "python",
    "bash": "bash",
    "sh": "bash",
    "shell": "bash",
    "zsh": "bash",
    "json": "json",
    "jsonc": "json",
    "text": "text",
    "txt": "text",
    "md": "text",
    "yaml": "yaml",
    "yml": "yaml",
    "mermaid": "mermaid",
}


def extract_file(path: Path, root: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    out = []
    for index, match in enumerate(FENCE_RE.finditer(text), start=1):
        raw_lang = (match.group(1) or "").strip().lower()
        lang = LANG_ALIASES.get(raw_lang, raw_lang or "unknown")
        body = match.group(2)
        if body.endswith("\n"):
            body = body[:-1]
        start_line = text.count("\n", 0, match.start()) + 1
        out.append(
            {
                "id": f"{rel}:{index}",
                "source": rel,
                "abs": str(path),
                "index": index,
                "lang": lang,
                "raw_lang": raw_lang,
                "start_line": start_line,
                "body": body,
            }
        )
    return out


def extract_trees(trees: list[tuple[Path, list[str]]]) -> list[dict]:
    samples = []
    for root, patterns in trees:
        root = root.resolve()
        for pattern in patterns:
            for path in sorted(root.glob(pattern)):
                if not path.is_file():
                    continue
                if any(part in {".git", "node_modules", "dist"} for part in path.parts):
                    continue
                samples.extend(extract_file(path, root))
    return samples


def default_samples() -> list[dict]:
    return extract_trees(
        [
            (
                Path("/tmp/calle-lab/calle-docs"),
                [
                    "content/guides/*.mdx",
                    "examples/*.py",
                    "README.md",
                    "AGENTS.md",
                ],
            ),
            (Path("/tmp/calle-lab"), ["doc-*.md"]),
        ]
    )


def main() -> None:
    samples = default_samples()
    out = Path("/tmp/calle-lab/lab-out/fences.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(samples, indent=2), encoding="utf-8")
    counts: dict[str, int] = {}
    for sample in samples:
        counts[sample["lang"]] = counts.get(sample["lang"], 0) + 1
    print(f"wrote {len(samples)} fences to {out}")
    for lang, count in sorted(counts.items()):
        print(f"  {lang}: {count}")


if __name__ == "__main__":
    main()
