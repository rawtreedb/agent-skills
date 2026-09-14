# RawTree Agent Skills

Agent Skills for RawTree-focused AI workflows.

This repository packages the RawTree skill and hosted MCP server for OpenAI
ChatGPT/Codex and Kiro. It uses the portable Agent Plugins format with OpenAI
listing metadata and generated Codex compatibility files. Kiro can install it
as the RawTree Power; compatible agents can also use `skills/` directly.

## Repository Structure

```text
plugin.json
mcp.json
.codex-plugin/plugin.json  # generated compatibility manifest
.mcp.json                 # generated compatibility MCP configuration
POWER.md
icon.png
scripts/package_plugin.py
docs/openai-submission.md
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
and starter prompts. Portable clients discover `skills/` and `mcp.json` at the
root. The generated `.codex-plugin/plugin.json` and `.mcp.json` support clients
using the Codex compatibility format. Both formats use the same hosted endpoint;
no local Node.js server or bundled credentials are required.

Build and check the package with Python 3.10 or later:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/package_plugin.py --check --build
```

This creates `dist/rawtree/` and `dist/rawtree.zip`, with the plugin manifest,
MCP configuration, icon, license, and complete skill references. CI runs the same
checks and attaches the ZIP to each successful workflow run.

After changing `plugin.json` or `mcp.json`, regenerate the compatibility files
with `python3 scripts/package_plugin.py`, then rerun the check/build command.
Edit the portable files rather than the generated copies.

For local testing, use `$plugin-creator` in Codex with the built
`dist/rawtree` folder and request a personal marketplace entry. Install RawTree
from that local source, authenticate its bundled MCP connection, and start a
new task. Confirm RawTree tools are available before running queries. The skill
can also be selected explicitly with `$rawtree`.

Public publication requires a separate OpenAI submission and review. The
[submission guide](docs/openai-submission.md) provides the endpoint, release
notes, test cases, and remaining account-dependent steps. A merged PR or local
marketplace installation does not publish the plugin.

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
