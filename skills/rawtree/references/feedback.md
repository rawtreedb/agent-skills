# Feedback

Feedback is available to agents as well as humans, including before an organization exists. Use the current connection's API URL and credentials. Feedback is stored by RawTree; it does not create a table in the user's database.

## Prepare the Report

1. Describe what you tried, what happened, and what you expected. Distinguish observed behavior from a suspected cause. Send one report per distinct issue during the task.
2. Set `actor_type` by authorship:
   - `agent` for an issue or observation you discovered while working.
   - `human` when the user asks you to send their feedback, even though you execute the submission.
   The credential's user or service-account identity does not determine authorship.
3. Choose `category`: `bug` for defects or inconsistencies, `feature_request` for improvements, `question` for unclear behavior, or `other` for remaining feedback.
4. Put relevant command or tool names, error codes, and reproduction details in the optional `extra` JSON object. Include only details safe to share with RawTree; omit credentials and private data. Nested JSON values are supported.
5. Include `organization_id` or `cluster_id` only when relevant, known, and accessible. Both are optional UUIDs. Scoped API keys and workload credentials supply their bound IDs; a supplied cluster determines its organization. With user credentials, selected organization/cluster names and database defaults are not automatically substituted for these fields. The server derives `user_id` or `service_account_id` from authentication.

Preparation is complete when the report is specific, sanitized, attributed to its author, and scoped only with verified IDs.

## Submit Through the Selected Client

Load the matching interface reference and verify its current contract:

| Surface | Interface | Contract |
|---|---|---|
| MCP | `submit-feedback` | [mcp.md](mcp.md) and the discovered tool schema |
| CLI | `rtree feedback` | [cli.md](cli.md) and `rtree feedback --help` |
| API | `POST /v1/feedback` | [api.md](api.md) and the selected API's OpenAPI specification |

The request requires `message`, `category`, and `actor_type`. Optional fields are `organization_id`, `cluster_id`, and `extra`. MCP and CLI send client identity in headers. Direct API clients can set `x-rawtree-client` and `x-rawtree-client-version`; client identity is not a feedback body field.

Example MCP arguments or API JSON body for an agent's observation:

```json
{
  "message": "The query error names a field absent from the submitted SQL. Expected the error to identify the failing expression.",
  "category": "bug",
  "actor_type": "agent",
  "extra": {
    "tool": "run-query",
    "error_code": "UNKNOWN_IDENTIFIER"
  }
}
```

CLI shape (`--extra` takes a JSON object value):

```bash
rtree feedback --category question --actor-type agent \
  --message 'The error does not explain which input needs to change.' \
  --extra '{"command":"query","expected":"actionable error guidance"}' \
  --json
```

If the tool or command is unavailable, report that limitation. Change clients, install updates, or authenticate only within the user's authorized scope.

## Verify and Continue

A successful submission returns `id` and `created_at` (HTTP `201` for the API). Keep that receipt and briefly tell the user what was reported, then continue their task when possible. Storage does not mean the issue is resolved or promise a reply.

Submissions are not deduplicated. After a timeout or interrupted response, treat delivery as uncertain and avoid automatic retries. Explain an unavailable or failed submission without blocking unrelated work.
