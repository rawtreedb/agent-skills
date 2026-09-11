# AGENTS.md

Guidance for agents working in this repository.

## Structure

```text
skills/
  {skill-name}/
    SKILL.md
```

## Notes

- Keep `skills/rawtree/SKILL.md` aligned with RawTree platform docs source when updating.
- Edit portable metadata in `plugin.json` and MCP configuration in `mcp.json`; regenerate the Codex compatibility files with `python3 scripts/package_plugin.py`.
- After packaging or skill-reference changes, run `python3 scripts/package_plugin.py --check --build`.
