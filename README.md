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

- `rawtree` — RawTree API and CLI guidance for database, ingestion, querying, and observability workflows.

## Examples

The `rawtree` skill activates automatically when a task involves RawTree. You
can also invoke it directly with `/rawtree` when it is installed as a
standalone skill in Kiro.

### Ask an agent

Try prompts such as:

- “Set up a RawTree database called `analytics` and explain the safest way to create an API key.”
- “Insert these signup events into an `events` table, then verify the insert with a bounded read-only query.”
- “Show the top event types in the last 24 hours and explain the query plan.”
- “Investigate failed inserts from the last hour and suggest how to fix them.”

When the RawTree MCP server is connected, the agent can use the appropriate
tools for table discovery, ingestion, querying, and logs.

### CLI workflow

```bash
# Authenticate and select a database
rtree login
rtree database create analytics
rtree database use analytics

# Ingest JSON; the table is created automatically on first insert
rtree insert --table events --data '{"event":"signup","user_id":1}'

# Run a bounded analytical query
rtree query --sql "SELECT event, count() FROM events GROUP BY event ORDER BY count() DESC LIMIT 10"
```

### Direct API workflow

Use an explicit API key for scripts and CI rather than an interactive login:

```bash
export RAWTREE_API_KEY="rt_..."
BASE_URL="https://api.rawtree.com"

curl -sS -X POST "$BASE_URL/v1/tables/events" \
  -H "Authorization: Bearer $RAWTREE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"event":"signup","user_id":1},{"event":"purchase","user_id":1,"amount":42}]'

curl -sS -X POST "$BASE_URL/v1/query" \
  -H "Authorization: Bearer $RAWTREE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT event, count() FROM events GROUP BY event ORDER BY count() DESC LIMIT 10"}'
```

RawTree query endpoints accept read-only SQL. For nested or mixed-type JSON,
the skill covers dynamic columns, dot notation, casts, `dynamicType`, and the
`__raw_data` virtual column.

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
