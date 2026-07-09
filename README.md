# RawTree Agent Skills

Agent Skills for RawTree-focused AI workflows.

## Repository Structure

```text
skills/
  rawtree/
    SKILL.md
```

## Install

```bash
npx skills add rawtreedb/agent-skills
```

## Available Skills

- `rawtree` — RawTree API and CLI guidance sourced from `backend/src/routes/docs.rs`.

## MCP Server

The Codex plugin registers RawTree's MCP server from [`@rawtree/mcp`](https://github.com/rawtreedb/rawtree-mcp) over stdio. Set `RAWTREE_API_KEY` where your agent runs.

## Plugins

This repo serves as a plugin for multiple platforms:

- **OpenAI Codex** — `.codex-plugin/`
- **Claude Code** — `.claude-plugin/`
- **Cursor** — `.cursor-plugin/`
