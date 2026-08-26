#!/usr/bin/env python3
"""Generate Kiro steering from the canonical RawTree Agent Skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "rawtree" / "SKILL.md"
TARGET = ROOT / "steering" / "rawtree.md"


def read_skill() -> tuple[str, str, str]:
    text = SOURCE.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{SOURCE} must start with YAML frontmatter")

    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{SOURCE} has no closing frontmatter delimiter")

    frontmatter = text[4:end]
    body = text[end + len("\n---\n") :].lstrip()

    def field(name: str) -> str:
        match = re.search(rf"^{re.escape(name)}:\s*(.+)$", frontmatter, re.MULTILINE)
        if not match:
            raise ValueError(f"{SOURCE} frontmatter is missing {name}")
        value = match.group(1).strip()
        if value.startswith('"'):
            return json.loads(value)
        return value

    return field("name"), field("description"), body


def render() -> str:
    name, description, body = read_skill()
    return (
        "---\n"
        "inclusion: auto\n"
        f"name: {name}\n"
        f"description: {json.dumps(description, ensure_ascii=False)}\n"
        "---\n\n"
          f"{body.rstrip()}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated output is stale")
    args = parser.parse_args()

    expected = render()
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != expected:
            print(f"{TARGET} is out of date; run this script without --check", file=sys.stderr)
            return 1
        return 0

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
