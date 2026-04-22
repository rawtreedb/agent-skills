---
name: rawtree
description: "Use when working with RawTree CLI and API workflows, including project setup, API key creation, ingest, query, logs, parameterized SQL, supported types, and error handling."
metadata:
  author: rawtree
  version: "0.1.0"
---

# RawTree

The content below is copied from `backend/src/routes/docs.rs` (`plain_text_docs`).

RAWTREE API — Agent-Friendly Analytics

Base URL: /v1

Machine-readable docs:
  OpenAPI spec (JSON): GET /v1/openapi.json
  Swagger UI:          GET /docs
  This document:       GET /v1/docs
  AI plugin manifest:  GET /.well-known/ai-plugin.json

## AUTHENTICATION


Sign in flow for users and agents:
  1) Run: rtree login
  2) Optionally create an explicit API key for scripts/services:
     rtree key create --project <project> --name <name> --permission read_write

Permission levels for API keys:
  admin, read_write, write_only, read_only

Rules of thumb:
  - Use rtree login for interactive auth and project/org management.
  - Use explicit API keys (rw_...) for programmatic API calls.
  - Query endpoints are read-only (SELECT-only validation).

## CLI QUICK START


Install (recommended):
  curl -sSf https://rawtree.com | sh

Default API URL used by CLI:
  https://api.rawtree.com

Common flows:
  # Sign in
  rtree login

  # Create/select project
  rtree project create analytics
  rtree project use analytics

  # Create an explicit API key for API usage
  rtree key create --project analytics --name api --permission read_write

  # Insert JSON (inline, file, or URL)
  rtree insert --table events --data '{"event":"signup","user_id":1}'
  rtree insert --table events --file ./events.jsonl
  rtree insert --table events --url https://example.com/events.jsonl

  # Optional built-in transforms for ingest
  # otlp-traces, otlp-logs, otlp-metrics, cloudwatch-logs, cloudtrail
  rtree insert --table traces --url https://example.com/otlp.json --transform otlp-traces

  # Query
  rtree query --sql "SELECT count() FROM events"
  rtree query "SELECT * FROM events LIMIT 10"

  # Logs
  rtree logs --project analytics --since 1h --type insert --status error --table events

  # API keys (command is singular: key)
  rtree key list --project analytics
  rtree key create --project analytics --name ci --permission read_write
  rtree key delete --project analytics <id_or_token>

  # Tables
  rtree table list --project analytics
  rtree table describe --project analytics events

Agent-friendly flags and env:
  --json                    # machine-readable output for most commands
  --api-url <url>           # override endpoint
  --org <organization>

  RAWTREE_URL=https://api.rawtree.com
  RAWTREE_TOKEN=rw_...
  RAWTREE_PROJECT=analytics
  RAWTREE_ORG=team_alpha

## CURL QUICK START


  BASE_URL="https://api.rawtree.com"
  # 1) Sign in and create key with CLI:
  #    rtree login
  #    rtree project create analytics
  #    rtree project use analytics
  #    rtree key create --project analytics --name api --permission read_write
  API_KEY="<rw_token_from_rtree_key_create>"

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

## API REFERENCE (AGENT-ORIENTED)


Projects:
  GET    /v1/projects
  POST   /v1/projects                 {"name": "..."} (or empty body for generated name)
  PATCH  /v1/projects/{project}       {"name": "..."}
  DELETE /v1/projects/{project}

Data query:
  POST /v1/query
  Body: {"sql":"SELECT ..."}
  Notes:
    - JSON response includes meta/data/rows/statistics and optional hints.
    - Read-only SQL only.

Logs:
  GET /v1/logs
  Query parameters:
    start_time, end_time, limit, offset, search
  search filter format:
    type:select|insert status:success|error table:table1,table2

Tables:
  GET    /v1/tables
  GET    /v1/tables/{table}
  POST   /v1/tables/{table}
  DELETE /v1/tables/{table}

Insert modes for POST /v1/tables/{table}:
  - JSON object body: {...}
  - JSON array body:  [{...},{...}]
  - URL ingest:       /v1/tables/{table}?url=<encoded_url>[&transform=<name>]
    URL ingest streams NDJSON progress events.

API keys:
  GET    /v1/keys
  POST   /v1/keys                        {"name","permission"}
  DELETE /v1/keys/{id_or_token}
  Notes:
    - Unscoped /v1/keys routes require admin API key auth.
    - id_or_token accepts UUID id or full rw_ token.

Health:
  GET /health

## PARAMETERIZED QUERIES


Use {param_name:Type} syntax in SQL to define parameters.

  SQL: SELECT * FROM events WHERE user = {user_id:String} LIMIT {n:UInt32}

Parameter types must be valid RawTree types (see SUPPORTED TYPES below).

In ad-hoc queries:
  POST /v1/query
  Body: {"sql":"SELECT * FROM events WHERE user = {user_id:String}","params":{"user_id":"alice"}}
  CLI:
    rtree query "SELECT * FROM events WHERE user = {user_id:String}"
    (params passed via the API body)

## SUPPORTED TYPES (RawTree)


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

When casting in queries, use standard RawTree functions or :: syntax:
  toUInt32(value), toString(value), toDate(value), toFloat64(value)
  CAST(value AS UInt32), CAST(value AS Array(String))
  value::Int64, column::String, column::Array(UInt32)

Example:
  SELECT user::String, value::Float64, inserted_at::Date FROM events

## QUERY TIPS


  - Only SELECT queries are allowed (read-only).
  - Standard SQL is supported.
  - Use dot notation to access nested JSON fields.
  - Common patterns:
      SELECT count() FROM events
      SELECT id, count() FROM events GROUP BY id
      SELECT id, count() FROM events GROUP BY id ORDER BY count() DESC LIMIT 10

## ERRORS


All errors return: {"error":"code","message":"...","hint":"..."}
The hint field contains actionable suggestions to fix the issue.

CLI exit codes:
  1 = authentication/authorization error (401, 403)
  2 = validation/bad request (400)
  3 = server/connection error (5xx)
  4 = not found (404)
  5 = general error

