# OpenAI submission

Use this guide when preparing the RawTree plugin for the
[OpenAI submission portal](https://platform.openai.com/plugins). Requirements
were checked against the [submission documentation](https://developers.openai.com/plugins/deploy/submission)
on September 11, 2026. This repository prepares the package; publication happens
after submission, OpenAI review, and a publisher-controlled release.

## Package and listing

Run the build command in [README.md](../README.md). Use `dist/rawtree/` for
local plugin testing and the bundled `skills/rawtree/` tree for the portal's
skill upload. `dist/rawtree.zip` contains the complete plugin, including the
skill and all six references.

Copy listing values and starter prompts from `plugin.json`; it is the source
of truth for the public metadata. The logo is `icon.png`. Support contact:
[contact@rawtree.com](mailto:contact@rawtree.com).

Choose **With MCP**, **Universal**, and the endpoint
`https://mcp.rawtree.com/mcp`. Configure OAuth for interactive sign-in. Submit
the endpoint directly; a registered integration ID is not a substitute for
an MCP submission. This package has no custom embedded UI.

Release notes for 0.2.0:

> Adds OpenAI listing metadata and Codex compatibility packaging to the RawTree
> plugin. Bundles the hosted MCP connection and shared workflow guidance for
> resource discovery, ingestion, SQL, Dynamic fields, and performance.

## Reviewer fixtures

Prepare a dedicated demo account with a disposable organization, cluster, and
default database. Record their exact names in the private submission. Give the
account access to a `plugin_events` table containing these three synthetic rows:

```json
{"event_id":"plugin-1","level":"error","latency_ms":125,"service":"checkout"}
{"event_id":"plugin-2","level":"info","latency_ms":"unknown","service":"checkout"}
{"event_id":"plugin-3","level":"error","service":"worker"}
```

Also provide a writable scratch table named `plugin_scratch` and a separate
read-only API key for the permission test. Supply credentials through the
portal's private credential fields. Reset scratch data between runs. Reviewer
sign-in must work without MFA, SMS, email confirmation, or private-network access.

## Positive test cases

These are expected behaviors to execute and record before submission, not
claims that authenticated tests have already passed.

| Prompt | Fixture | Expected workflow and result |
| --- | --- | --- |
| “Using RawTree, list my organizations, then the clusters and databases in the demo organization.” | Demo OAuth account and its recorded organization name | Use organization, cluster, then database discovery tools. Return names and identifiers from tool results. |
| “Describe `plugin_events` in the demo database and show at most three rows.” | Demo account; `plugin_events` | Inspect the table, then run a bounded read-only query. Return the observed schema and no more than three rows. |
| “Count the error events in `plugin_events` by service.” | Three fixture rows | Load MCP and query guidance, inspect relevant Dynamic types, and aggregate with suitable casts. Return checkout: 1 and worker: 1. |
| “Calculate average numeric `latency_ms` in `plugin_events` and explain excluded values.” | Mixed-type and missing latency fixture | Load Dynamic guidance, use the observed numeric type, and account for the string and missing value. Return 125 for the numeric subset and explain the two excluded rows. |
| “Insert this one event into `plugin_scratch` and verify it: event_id `plugin-write-1`, level `info`.” | Demo account with write permission; reset scratch table | Perform the scoped insert, inspect the result for partial failure, then read back the event. Return confirmed inserted data or a precise failure. |

## Negative test cases

| Prompt or scenario | Expected behavior | Reason |
| --- | --- | --- |
| Ask to list RawTree databases while signed out. | Explain the authentication requirement and route to the configured plugin connection. Report no discovered resources until tools succeed. | Configuration alone does not prove access. |
| “Clean up old RawTree data” without naming a database or table. | Clarify the exact target and operation before any deletion. | Neither the target nor destructive scope is authorized. |
| Attempt the scratch insert using only the read-only API key. | Report the permission failure and required write authority; do not switch credentials or claim success. | The provided credential does not authorize writes. |

## Finish in the portal

1. Select the publishing organization, verify its developer/business identity,
   and confirm the submitter has **Apps Management: Write**.
2. Confirm the listing's support, privacy, and terms links match that identity.
   Select supported countries using the publisher's actual availability.
3. Complete the generated domain verification challenge on the MCP host or an
   allowed parent host. Preserve any existing challenge needed by another plugin.
4. Configure reviewer authentication, scan tools, and verify every tool's
   `readOnlyHint`, `openWorldHint`, and `destructiveHint` against its behavior.
   Resolve scan errors in the owning MCP service before rescanning.
5. Upload the tested skill tree, run all eight cases above, and record observed
   results. Confirm OAuth scope/UserInfo requirements if workspace domain
   restrictions are needed.
6. Review the final listing, credentials, tool scan, skills, availability, and
   policy attestations. Submit for review; publish after approval.

Identity verification, demo credentials, country selection, domain challenges,
and authenticated tool results are external to this repository and remain to
be completed by the publisher.
