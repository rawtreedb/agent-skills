---
name: rawtree
description: "Use when working with RawTree CLI and API workflows, including database setup, API key creation, ingest, query, dynamic columns, query optimization, logs, parameterized SQL, supported types, bulk ingest, schema inspection, HTTP client setup, and error handling."
metadata:
  author: rawtree
  version: "0.4.0"
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

## Http Clients And User-Agent

Send an explicit `User-Agent` from programmatic clients. The CDN in front of the API
rejects Python's standard-library default before the request reaches the application:

```bash
curl -sS -A "Python-urllib/3.14" https://api.rawtree.com/health
# error code: 1010        <- HTTP 403, plain text, not JSON

curl -sS -A "my-app/1.0" https://api.rawtree.com/health
# {"status":"ok"}         <- HTTP 200
```

It applies to every endpoint, including unauthenticated `/health`, so it looks like an
authentication failure but is not — no API key is involved. `requests`, `httpx`, `curl`
and Go's default agent are unaffected; only the `Python-urllib/*` signature is blocked.

If you use `urllib` from the standard library, set the header:

```python
import json, urllib.request

req = urllib.request.Request(
    f"{BASE_URL}/v1/tables/events",
    data=json.dumps([{"event": "signup", "user_id": 1}]).encode(),
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "my-app/1.0",  # required: the urllib default is rejected
    },
    method="POST",
)
urllib.request.urlopen(req)
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

The request body must be **one JSON value** — an object or an array. Newline-delimited
JSON is *not* accepted here, even though `rtree insert --file events.jsonl` and URL
ingest both take it; posting NDJSON directly fails with
`{"error":"bad_request","message":"Invalid JSON body."}`. Wrap the lines in an array.

A successful insert returns the row count: `{"inserted": 3}`.

Data endpoints accept `?database=<database>` (and `?organization=<organization>`);
without them the key's default database is used.

`DELETE /v1/tables/{table}` requires an **`admin`** key; `read_write` is not enough and
returns `{"error":"forbidden","hint":"Deleting tables requires admin permission."}`. Plan
for this when handing a service a key — a `read_write` key can create tables it cannot
drop.

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

## Bulk Ingest

Batch rows into one request. A single-row insert costs roughly one second end to end, so
inserting a row per request is about **1 row/s**, while a few thousand rows in one request
is **thousands of rows/s** — a three-orders-of-magnitude difference, not a micro-optimisation.

```bash
# Slow: one request per row (~1 row/s)
for row in "${rows[@]}"; do
  curl -X POST "$BASE_URL/v1/tables/events" -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" -d "$row"
done

# Fast: one request per batch (measured ~3.5k rows/s for 5,000-row batches)
curl -X POST "$BASE_URL/v1/tables/events" -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" -d "$(jq -s '.' rows.jsonl)"
```

Large bodies are fine — a 60 MB / 66,000-row array inserts in about 12 s. For a big load,
batch in the low thousands of rows and stream batch by batch rather than building one
enormous body. For files and remote data prefer `rtree insert --file` / `--url`, which
handle the batching for you.

## Inspecting Tables And Schema

Use `DESCRIBE TABLE <table>` or `GET /v1/tables/{table}` to see inferred columns.

**Do not use `system.columns` to discover a table's shape.** Physically the table holds one
`JSON` column, so `system.columns` reports exactly one row — `__raw_data` — while `DESCRIBE`
reports every inferred field:

```sql
SELECT name, type FROM system.columns WHERE table = 'events'  -- 1 row:  __raw_data  JSON
DESCRIBE TABLE events                                         -- every field, as Dynamic
```

Both are telling the truth about different things, but only `DESCRIBE` answers "what can I
select?". The fields are queryable as ordinary bare columns regardless
(`SELECT user_id FROM events`), and each reports type `Dynamic` — see Dynamic Columns.

`SHOW CREATE TABLE` is rejected: read queries must start with SELECT, WITH, EXPLAIN or DESCRIBE.

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

API errors return: `{"error":"code","message":"...","hint":"..."}`
The hint field contains actionable suggestions to fix the issue.

A response whose body is **not** JSON did not come from the API — it was rejected at the
edge before reaching it. The common case is a `403` with the plain-text body
`error code: 1010`, which means the CDN blocked the request's `User-Agent`; see
"Http Clients And User-Agent" above. Do not read it as an invalid or expired API key.

CLI exit codes:

- `1` = authentication/authorization error (401, 403)
- `2` = validation/bad request (400)
- `3` = server/connection error (5xx)
- `4` = not found (404)
- `5` = general error
