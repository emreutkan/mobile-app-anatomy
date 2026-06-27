#!/usr/bin/env python3
"""Compile the modular mobile-app-anatomy atlas into GOD_README.md."""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
import re
import sys

DEFAULT_TOP_LEVEL = [
    "EXECUTIVE_SUMMARY.md",
    "DISCOVERY_JOURNAL.md",
    "COVERAGE.md",
    "UNKNOWNS.md",
    "CONTRADICTIONS.md",
    "GLOSSARY.md",
]
DEFAULT_SECTIONS = [
    "00-product",
    "01-launch-auth-onboarding",
    "02-navigation",
    "03-screens",
    "04-features",
    "05-flows",
    "06-state-data",
    "07-platform",
    "08-runtime",
    "09-code-atlas",
]


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    return text[end + 5 :]


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1)
    return fallback


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"[\s-]+", "-", value)
    return value.strip("-") or "section"


def source_documents(root: Path, include_chunks: bool) -> list[Path]:
    docs: list[Path] = []
    for name in DEFAULT_TOP_LEVEL:
        path = root / name
        if path.is_file():
            docs.append(path)

    for section in DEFAULT_SECTIONS:
        section_dir = root / section
        if not section_dir.is_dir():
            continue
        docs.extend(sorted(p for p in section_dir.rglob("*.md") if p.name != "GOD_README.md"))

    evidence = root / "evidence"
    if evidence.is_dir():
        for sub in ("files", "runtime"):
            d = evidence / sub
            if d.is_dir():
                docs.extend(sorted(p for p in d.rglob("*.md")))
        if include_chunks:
            d = evidence / "chunks"
            if d.is_dir():
                docs.extend(sorted(p for p in d.rglob("*.md")))

    seen: set[Path] = set()
    unique: list[Path] = []
    for path in docs:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(path)
    return unique


def compile_readme(root: Path, output: Path, title: str, include_chunks: bool) -> int:
    documents = source_documents(root, include_chunks)
    if not documents:
        print(f"No source Markdown documents found under {root}", file=sys.stderr)
        return 2

    entries: list[tuple[Path, str, str]] = []
    used_slugs: dict[str, int] = {}
    for path in documents:
        text = strip_frontmatter(path.read_text(encoding="utf-8", errors="replace")).strip()
        if not text:
            continue
        heading = first_heading(text, path.stem.replace("-", " ").title())
        base_slug = slugify(heading)
        count = used_slugs.get(base_slug, 0) + 1
        used_slugs[base_slug] = count
        slug = base_slug if count == 1 else f"{base_slug}-{count}"
        entries.append((path, heading, slug))

    generated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    out: list[str] = [
        f"# {title}",
        "",
        "> This file is a compiled view of the modular mobile-app anatomy atlas. ",
        "> The modular source documents and machine ledger remain authoritative.",
        "",
        f"Generated: `{generated}`",
        "",
        "## Table of contents",
        "",
    ]

    for _, heading, slug in entries:
        out.append(f"- [{heading}](#{slug})")

    out.extend(["", "---", ""])

    for path, heading, slug in entries:
        text = strip_frontmatter(path.read_text(encoding="utf-8", errors="replace")).strip()
        lines = text.splitlines()
        if lines and re.match(r"^#\s+", lines[0]):
            lines[0] = f"## {heading}"
        else:
            lines.insert(0, f"## {heading}")
        # Add an explicit HTML anchor so duplicate titles remain stable.
        out.append(f'<a id="{slug}"></a>')
        out.append("")
        out.extend(lines)
        out.extend([
            "",
            f"_Source: `{path.relative_to(root).as_posix()}`_",
            "",
            "---",
            "",
        ])

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(f"Compiled {len(entries)} documents into {output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="Anatomy output directory")
    parser.add_argument("--output", help="Output file; defaults to <out>/GOD_README.md")
    parser.add_argument("--title", default="Mobile Application Anatomy Atlas")
    parser.add_argument("--include-chunks", action="store_true", help="Include verbose line-shard reports")
    args = parser.parse_args()

    root = Path(args.out).resolve()
    output = Path(args.output).resolve() if args.output else root / "GOD_README.md"
    return compile_readme(root, output, args.title, args.include_chunks)


if __name__ == "__main__":
    raise SystemExit(main())
