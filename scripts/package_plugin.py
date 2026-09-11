#!/usr/bin/env python3
"""Generate Codex compatibility files and build the portable RawTree package."""

import argparse
import json
from pathlib import Path
import re
import shutil
import zipfile

import yaml


ROOT = Path(__file__).resolve().parents[1]


def compatibility_files():
    manifest = json.loads((ROOT / "plugin.json").read_text())
    mcp = json.loads((ROOT / "mcp.json").read_text())
    legacy = {key: value for key, value in manifest.items()
              if key not in ("$schema", "extensions")}
    legacy.update(manifest["extensions"]["com.openai"])
    legacy.update(skills="./skills/", mcpServers="./.mcp.json")
    servers = {}
    for name, config in mcp["mcpServers"].items():
        if config["type"] != "streamable-http":
            raise ValueError(f"Unsupported MCP transport for {name}: {config['type']}")
        servers[name] = {**config, "type": "http"}
    return {
        ".codex-plugin/plugin.json": legacy,
        ".mcp.json": {"mcpServers": servers},
    }


def validate_skills():
    for skill in sorted((ROOT / "skills").iterdir()):
        if not skill.is_dir():
            continue
        text = (skill / "SKILL.md").read_text()
        if not text.startswith("---\n"):
            raise ValueError(f"Missing skill frontmatter: {skill.name}")
        frontmatter = yaml.safe_load(text.split("---", 2)[1])
        if frontmatter.get("name") != skill.name or not frontmatter.get("description"):
            raise ValueError(f"Invalid skill name or description: {skill.name}")
        yaml.safe_load((skill / "agents/openai.yaml").read_text())
        for document in skill.rglob("*.md"):
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text()):
                if ":" in target or target.startswith("#"):
                    continue
                resolved = (document.parent / target.split("#", 1)[0]).resolve()
                if not resolved.is_relative_to(skill.resolve()) or not resolved.is_file():
                    raise ValueError(f"Broken or non-portable skill reference: {document}: {target}")


def build():
    manifest = json.loads((ROOT / "plugin.json").read_text())
    name = manifest["name"]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("Plugin name must be lowercase hyphen-case")
    output = ROOT / "dist" / name
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    files = [ROOT / path for path in (
        "plugin.json", "mcp.json", ".codex-plugin/plugin.json", ".mcp.json",
        "icon.png", "LICENSE", "POWER.md",
    )]
    files.extend(path for path in (ROOT / "skills").rglob("*") if path.is_file())
    for source in files:
        if source.is_symlink():
            raise ValueError(f"Package files must be regular files: {source}")
        target = output / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    archive = ROOT / "dist" / f"{name}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(output.rglob("*")):
            if path.is_file():
                # Fixed metadata makes the same source produce the same archive.
                info = zipfile.ZipInfo(path.relative_to(output.parent).as_posix())
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                bundle.writestr(info, path.read_bytes())
    print(f"Built {output} and {archive}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated files are stale")
    parser.add_argument("--build", action="store_true", help="Also build dist/rawtree and its ZIP")
    args = parser.parse_args()
    for relative, payload in compatibility_files().items():
        path = ROOT / relative
        expected = json.dumps(payload, indent=2) + "\n"
        if args.check:
            if not path.is_file() or path.read_text() != expected:
                raise ValueError(f"Stale {relative}; run python3 scripts/package_plugin.py")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected)
    validate_skills()
    print("Compatibility files and skill references validated")
    if args.build:
        build()


if __name__ == "__main__":
    main()
