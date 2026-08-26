# RawTree Agent Skills

Agent Skills for RawTree-focused AI workflows.

This repository is also a portable Agent Plugins package. Kiro can install it
as the RawTree Power, while other compatible coding agents can continue to
discover the skills under `skills/`.

## Repository Structure

```text
plugin.json
mcp.json
skills/
  rawtree/
    SKILL.md
```

## Available Skills

- `rawtree` — RawTree API and CLI guidance sourced from `backend/src/routes/docs.rs`.

## Kiro Power

The root `plugin.json` follows Agent Plugins 1.0 and makes this repository
installable as a Kiro Power. The existing `skills/rawtree/SKILL.md` remains the
single source of truth for RawTree guidance; it is not duplicated into a
second Power repository.

The root `mcp.json` connects the Power to RawTree's hosted Streamable HTTP MCP
server at `https://mcp.rawtree.com/mcp`. Kiro manages the MCP connection and
authentication. No API keys or authorization headers are stored in this
repository.

For local MCP development, continue to use the setup in the
[`rawtree-mcp` repository](https://github.com/rawtreedb/rawtree-mcp), which
supports both stdio and a local HTTP server.

### Install in Kiro

In Kiro, open **Powers → Add Custom Power → Import power from GitHub** and
provide this repository URL. For local testing, use **Import power from a
folder** after cloning the repository.
