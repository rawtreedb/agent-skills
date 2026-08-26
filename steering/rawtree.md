---
inclusion: auto
name: rawtree
description: "Use when working with RawTree CLI and API workflows, including database setup, API key creation, ingest, query, dynamic columns, query optimization, logs, parameterized SQL, supported types, and error handling."
---

# RawTree

## RawTree Api — Agent-Friendly Analytics

Base URL: `https://api.rawtree.com/v1`

### Machine-readable docs

- OpenAPI spec (JSON): `GET https://api.rawtree.com/v1/openapi.json`

## Authentication

Sign in flow for users and agents:

1. Run: `rtree login`
2. Optionally create an explicit API key for scripts/services:
   `rtree key create --database <database> --name <name> --permission read_write`

Permission levels for API keys:

- `admin`, `read_write`, `write_only`, `read_only`

Rules of thumb:

- Use `rtree login` for interactive auth and database/org management.
- Use explicit API keys (`rt_...`) for programmatic API calls.
- Query endpoints are read-only (SELECT-only validation).

## Cli Quick Start

Install (recommended):

```bash
curl -sSf https://rawtree.com | sh
```

Default API URL used by CLI:

```text
https://api.rawtree.com
```

Common flows:

```bash
# Sign in
rtree login

# Create/select database
rtree database create analytics
rtree database use analytics

# Create an explicit API key for API usage
rtree key create --database analytics --name api --permission read_write

# Insert JSON (inline, file, or URL)
rtree insert --table events --data '{"event":"signup","user_id":1}'
rtree insert --table events --file ./events.jsonl
rtree insert --table events --url https://example.com/events.jsonl

# Optional built-in transforms for ingest
# otlp-traces, otlp-logs, otlp-metrics, cloudwatch-logs, cloudtrail, firehose
rtree insert --table traces --url https://example.com/otlp.json --transform otlp-traces

# Query
rtree query --sql "SELECT count() FROM events"
rtree query "SELECT * FROM events LIMIT 10"

# Logs
rtree logs --database analytics --since 1h --type insert --status error --table events

# API keys (command is singular: key)
rtree key list --database analytics
rtree key create --database analytics --name ci --permission read_write
rtree key delete --database analytics <id_or_token>

# Tables
rtree table list --database analytics
rtree table describe --database analytics events
```

Agent-friendly flags and env:

```text
--json                    # machine-readable output for most commands
--api-key <api-key>       # API key for non-interactive use
--api-url <url>           # override endpoint
--database <database>
--org <organization>

RAWTREE_API_KEY=rt_...
RAWTREE_API_URL=https://api.rawtree.com
RAWTREE_DATABASE=analytics
RAWTREE_ORG=team_alpha
```

## Curl Quick Start

```bash
BASE_URL="https://api.rawtree.com"
# 1) Sign in and create key with CLI:
#    rtree login
#    rtree database create analytics
#    rtree database use analytics
#    rtree key create --database analytics --name api --permission read_write
API_KEY="<rt_token_from_rtree_key_create>"

# 2) Insert rows (table auto-created on first insert)
curl -X POST "$BASE_URL/v1/tables/events" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"event":"signup","user_id":1},{"event":"purchase","user_id":1,"amount":42}]'

# 3) Query
curl -X POST "$BASE_URL/v1/query" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT event, count() FROM events GROUP BY event ORDER BY count() DESC"}'
```

## Api Reference (Agent-Oriented)

### Databases

- `GET /v1/databases`
- `POST /v1/databases` `{"name": "..."}`
- `DELETE /v1/databases/{database}`

### Data query

- `POST /v1/query`
- Body: `{"sql":"SELECT ..."}`
- Notes:
  - JSON response includes meta/data/rows/statistics and optional hints.
  - Read-only SQL only.

### Logs

- `GET /v1/logs`
- Query parameters:
  - `start_time`, `end_time`, `limit`, `offset`, `search`
- search filter format:
  - `type:select|insert|describe|explain status:success|error table:table1,table2`

### Tables

- `GET /v1/tables`
- `GET /v1/tables/{table}`
- `POST /v1/tables/{table}`
- `DELETE /v1/tables/{table}`

Insert modes for `POST /v1/tables/{table}`:

- JSON object body: `{...}`
- JSON array body: `[{...},{...}]`
- URL ingest: `/v1/tables/{table}?url=<encoded_url>[&transform=<name>]`
  URL ingest streams NDJSON progress events.

### API keys

- `GET /v1/keys`
- `POST /v1/keys` `{"name","permission"}`
- `DELETE /v1/keys/{id_or_token}`
- Notes:
  - JWT calls require `?organization=<organization>&database=<database>`.
  - API key calls require an admin database API key.
  - `id_or_token` accepts UUID id or full `rt_` token.

### Health

- `GET /health`

## Parameterized Queries

RawTree query requests accept `{"sql":"..."}` only. There is no `params` request-body field; treat parameterization as an application-level pattern.

Build the final SQL in code, then send it in the `sql` field. Escape or validate app-provided values before embedding them.

```bash
BASE_URL="https://api.rawtree.com"
API_KEY="<rt_token>"
USER_ID="alice"
N="10"

SQL=$(printf "SELECT * FROM events WHERE user = '%s' LIMIT %s" "$USER_ID" "$N")

curl -X POST "$BASE_URL/v1/query" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"sql\":\"$SQL\"}"
```

## Supported Types

```text
Integers:   UInt8, UInt16, UInt32, UInt64, UInt128, UInt256
            Int8, Int16, Int32, Int64, Int128, Int256
Floats:     Float32, Float64
Decimal:    Decimal(P, S), Decimal32(S), Decimal64(S), Decimal128(S)
Boolean:    Bool
Strings:    String, FixedString(N)
Dates:      Date, Date32, DateTime, DateTime64(precision)
UUID:       UUID
Arrays:     Array(T)            e.g. Array(String), Array(UInt32)
Tuples:     Tuple(T1, T2, ...)  e.g. Tuple(String, UInt32)
Maps:       Map(K, V)           e.g. Map(String, UInt64)
Nullable:   Nullable(T)         e.g. Nullable(String)
Enums:      Enum8('a'=1,'b'=2), Enum16(...)
LowCard:    LowCardinality(T)  e.g. LowCardinality(String)
IP:         IPv4, IPv6
```

When casting in queries, use standard RawTree functions or `::` syntax:

```sql
toUInt32(value), toString(value), toDate(value), toFloat64(value)
CAST(value AS UInt32), CAST(value AS Array(String))
value::Int64, column::String, column::Array(UInt32)
```

Example:

```sql
SELECT user::String, value::Float64, inserted_at::Date FROM events
```

## Dynamic Columns

Tables have no fixed schema. Columns are created automatically from ingested JSON, and every column is dynamic: each value keeps its own concrete type (`Int64`, `String`, `Float64`, ...). The same field can hold different types across rows.

- Reference columns directly by name: `SELECT action, user FROM events`.
- Use dot notation for nested JSON fields: `SELECT user.id FROM events`.
- Inspect the concrete type of each value with `dynamicType`:

```sql
SELECT value, dynamicType(value) AS value_type FROM events LIMIT 5
```

Semantics to rely on:

- `ORDER BY`, `GROUP BY`, `DISTINCT`, and aggregates work natively on dynamic columns and compare by value: integer `1`, float `1.0`, and integers of different widths sort and group as the same value.
- Functions and aggregates skip rows whose concrete type they cannot process. `sum(value)` over a column mixing numbers and strings sums the numbers; the response includes a hint listing the skipped types. Read hints to detect mixed-type fields.
- Cast inline when one specific type is needed (`value::Float64`, `toString(user)`); no schema change required.

## Write Queries the Optimizer Can Use

There are no indexes, primary keys, or materialized views to define. The engine builds primary keys automatically from the ingested data and rebuilds them based on real query access patterns; repeatedly executed slow aggregations get automatic projections. To benefit:

- Filter on bare columns so the auto-built primary key can prune: `WHERE user_id = 5`, `WHERE latency_ms > 1000`.
- Do not wrap filter columns in functions (`WHERE toString(user_id) = '5'`); computed expressions cannot use the index. Cast the literal side instead, or cast only in the SELECT list.
- Keep recurring queries stable in shape: the same repeated GROUP BY gets a projection and becomes fast automatically after a few runs.

## Original Row Payloads

Each row's original JSON is kept in the virtual `__raw_data` column. Use it to debug ingestion, check inferred fields, or recover exact source payloads — not as the normal query path (bare columns are faster and index-eligible).

```sql
SELECT __raw_data FROM events LIMIT 10
SELECT __raw_data.user.id FROM events LIMIT 10
```

## Query Tips

- Only read queries are allowed: statements must start with SELECT, WITH, EXPLAIN, or DESCRIBE.
- Standard SQL is supported.
- Common patterns:

```sql
SELECT count() FROM events
SELECT id, count() FROM events GROUP BY id
SELECT id, count() FROM events GROUP BY id ORDER BY count() DESC LIMIT 10
```

## Errors

All errors return: `{"error":"code","message":"...","hint":"..."}`
The hint field contains actionable suggestions to fix the issue.

CLI exit codes:

- `1` = authentication/authorization error (401, 403)
- `2` = validation/bad request (400)
- `3` = server/connection error (5xx)
- `4` = not found (404)
- `5` = general error
