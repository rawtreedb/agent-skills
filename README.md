# RawTree Agent Skills

Agent Skills for RawTree-focused AI workflows.

This repository is also a portable Agent Plugins package. Kiro can install it
as the RawTree Power, while other compatible coding agents can continue to
discover the skills under `skills/`.

## Repository Structure

```text
plugin.json
mcp.json
POWER.md
icon.png
skills/
  rawtree/
    SKILL.md
```

## Available Skills

- `rawtree` — RawTree guidance for database, ingestion, querying, dynamic-column, and observability workflows.

## Examples

The `rawtree` skill activates automatically when a task involves RawTree. In
Kiro, you can also invoke it directly with `/rawtree` when it is installed as
a standalone skill. Other compatible agents can discover it from
`skills/rawtree/SKILL.md`.

### Ask an agent

Try prompts such as:

- “Use the RawTree skill to plan an analytics workflow for evolving event data.”
- “Use the RawTree skill to design an ingestion workflow for logs, traces, and metrics.”
- “Use the RawTree skill to review this query for safe, bounded, read-only analysis.”
- “Use the RawTree skill to explain how dynamic columns handle nested and mixed-type JSON.”
- “Use the RawTree skill to investigate a failed ingestion and suggest the next diagnostic steps.”
- “Use the RawTree skill to review this RawTree integration for safety and performance issues.”

When the RawTree MCP server is connected, the agent can use the appropriate
tools for table discovery, ingestion, querying, and logs while following the
skill's guidance.

## Kiro Power

The root `plugin.json` follows Agent Plugins 1.0 and makes this repository
installable as a Kiro Power. The existing `skills/rawtree/SKILL.md` remains the
single source of truth for RawTree guidance; it is not duplicated into a
second Power repository.

The root `POWER.md` provides Kiro's legacy presentation metadata, including
the human-readable display name **RawTree**, description, keywords, and author.
It is retained for compatibility with local Power installation while
`plugin.json` remains the portable package manifest.

The root `mcp.json` uses the Agent Plugins 1.0 MCP schema and connects the
Power to RawTree's hosted Streamable HTTP MCP server at
`https://mcp.rawtree.com/mcp`. Kiro manages the MCP connection and
authentication. No API keys or authorization headers are stored in this
repository.

The repository also includes `icon.png`, RawTree's branded Power asset. Kiro's
custom GitHub and local Power imports currently use a generic placeholder icon;
the asset is available for registry curation or a local Kiro registry entry.

For local MCP development, continue to use the setup in the
[`rawtree-mcp` repository](https://github.com/rawtreedb/rawtree-mcp), which
supports both stdio and a local HTTP server.

## Support

For support with the RawTree Power or MCP integration, contact
[contact@rawtree.com](mailto:contact@rawtree.com).

See the [Tinybird Privacy Policy](https://www.tinybird.co/privacy) for
information about privacy and data handling.

### Install in Kiro

In Kiro, open **Powers → Add Custom Power → Import power from GitHub** and
provide this repository URL. For local testing, use **Import power from a
folder** after cloning the repository.
