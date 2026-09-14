# RawTree Agent Skills

Agent Skills for RawTree-focused AI workflows.

This repository packages the RawTree skill and hosted MCP server for OpenAI
ChatGPT/Codex and Kiro using the portable Agent Plugins format. Kiro can install
it as the RawTree Power; compatible agents can also use `skills/` directly.

## Repository Structure

```text
plugin.json
mcp.json
POWER.md
icon.png
skills/
  rawtree/
    SKILL.md
    agents/
      openai.yaml
    references/
      api.md
      cli.md
      dynamic-fields.md
      mcp.md
      performance.md
      query.md
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

- “Using RawTree, plan a workflow for evolving event data.”
- “Design a RawTree ingestion workflow for logs, traces, and metrics.”
- “Review this RawTree SQL query for bounded, read-only analysis.”
- “Explain how RawTree Dynamic fields handle nested and mixed-type JSON.”
- “Using RawTree MCP tools, describe this table and write a bounded query.”

When the RawTree MCP server is connected, the agent can use the appropriate
tools for table discovery, ingestion, querying, and logs while following the
skill's guidance.

## OpenAI plugin

### Install in Codex

Add this repository as a marketplace, then install RawTree:

```bash
codex plugin marketplace add rawtreedb/agent-skills
codex plugin add rawtree@rawtree
```

In the Codex app, you can also use **Add marketplace** with this repository's
GitHub URL, then select RawTree from the added source. Authenticate the bundled
MCP connection when prompted and start a new task to use the plugin.

The catalog at `.agents/plugins/marketplace.json` points to the plugin at the
repository root. No separate copy of the plugin is needed.

### Package

The root `plugin.json` is canonical. Its `extensions.com.openai.interface`
provides the listing descriptions, publisher, policy links, icon, capabilities,
and starter prompts. Portable clients discover the bundled `skills/` and
`mcp.json` at the root. The MCP configuration uses RawTree's hosted endpoint, so
the package needs no local server or bundled credentials.

For public publication, submit the plugin through OpenAI's **With MCP** flow
using `https://mcp.rawtree.com/mcp`, upload the `skills/rawtree` skill, and
complete the required listing, authentication, tool scan, and review tests.

Packaging follows [OpenAI's plugin documentation](https://developers.openai.com/plugins/build/plugins).

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
