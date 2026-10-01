---
book: The Complete DevOps Engineering Book
volume: 15
volume_title: "Observability and Telemetry"
chapter: 149
title: "Elastic, OpenSearch and CloudWatch"
slug: elastic-opensearch-and-cloudwatch
status: complete
summary: ../../_ai/chapter-summaries/149-elastic-opensearch-and-cloudwatch.md
---

# Chapter 149 — Elastic, OpenSearch and CloudWatch

**Section outline:** map events for exact and text search; run a bounded search procedure; execute a CloudWatch query with explicit billing scope; compare operational ownership; recover from mapping failures and missing ingestion.

Prerequisite: [trace investigation](148-tempo-jaeger-and-trace-investigation.md). This chapter adds searchable event workflows rather than replacing metrics or transactional order records.

## Search-oriented log workflows

Loki's bounded-stream model is not the only way to retain logs. Elasticsearch and OpenSearch support document-oriented search with explicit field mappings and indexed query behavior. A team investigating arbitrary event fields across many services may value this search model. It also takes on ingestion pipelines, schema management, shard placement, storage lifecycle and access controls. Choosing a powerful query language does not eliminate those responsibilities.

A mapping determines the meaning of a field. An outcome code such as `provider_timeout` is naturally an exact-value field. A human-oriented message can be analyzed for full-text search. A timestamp must be represented as a date to support time-range operations rather than relying on lexicographic string behavior. Numbers should remain numbers when used for range filters and aggregation. An unreviewed dynamic mapping can choose a type from the first observed document and reject a later document whose shape differs.

Keep event vocabulary consistent with Chapter 146. A producer emits `notification_retry_scheduled` and a bounded outcome code, not a free-form concatenation of order ID and exception. Retain the original event under access control, but select only the fields needed for ordinary incident search. A field's indexability and its privacy implications are separate decisions. Disabling indexing does not necessarily remove the field from retained source data.

Elastic and OpenSearch have related historical roots, but their releases, plugins, security features and API behavior have diverged. Do not treat them as interchangeable endpoints merely because a simple query works in both. Test the selected release's mapping, ingestion, authentication and lifecycle behavior. Kibana and OpenSearch Dashboards are their respective investigative interfaces; a saved UI filter should have the same population and field meaning as the underlying query.

## A bounded search procedure

This exercise assumes an **already provisioned isolated development** Elasticsearch or OpenSearch endpoint with an operator-authorized console, a disposable index namespace and access to the product's developer query console. It intentionally uses that console's HTTP-request notation rather than embedding credentials in curl. The endpoint's provisioning and authentication are environmental prerequisites: do not point these mutation examples at a shared production index. Creating an index and document changes retained state and consumes storage.

Create a uniquely named disposable index in the console, choosing a name that does not already exist. This example uses `dispatchdesk-lab-events` and must be changed if that name is occupied:

```text
PUT /dispatchdesk-lab-events
{
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "@timestamp": {"type": "date"},
      "service": {"type": "keyword"},
      "event": {"type": "keyword"},
      "outcome": {"type": "keyword"},
      "order_ref": {"type": "keyword"},
      "attempt": {"type": "integer"},
      "message": {"type": "text"}
    }
  }
}
```

Strict dynamic mapping makes unexpected fields a visible ingestion failure rather than silently expanding the schema. This is useful for the exercise, but production pipelines may need a deliberate strategy for optional extension fields. Inspect the actual acknowledgment response and then retrieve the mapping. A successful HTTP exchange alone does not prove that the document contract matches the producer.

Insert a representative event with a deterministic lab ID:

```text
PUT /dispatchdesk-lab-events/_doc/lab-event-1?refresh=wait_for
{
  "@timestamp": "2026-10-01T09:05:00Z",
  "service": "dispatchdesk-worker",
  "event": "notification_retry_scheduled",
  "outcome": "provider_timeout",
  "order_ref": "example-order-17",
  "attempt": 3,
  "message": "Provider did not acknowledge within the attempt deadline"
}
```

The fixed timestamp is an illustrative incident event, not a measured record. The explicit ID makes repeated execution replace that lab document rather than creating unbounded duplicates. `refresh=wait_for` waits for the write's visibility under the endpoint's refresh behavior; it is not a request to flush a backup or prove durability under host loss. Do not use forced refresh per production log event without measuring its impact.

Search the intended event population:

```text
GET /dispatchdesk-lab-events/_search
{
  "size": 20,
  "sort": [{"@timestamp": "asc"}],
  "query": {
    "bool": {
      "filter": [
        {"term": {"service": "dispatchdesk-worker"}},
        {"term": {"outcome": "provider_timeout"}},
        {"range": {"@timestamp": {
          "gte": "2026-10-01T09:00:00Z",
          "lt": "2026-10-01T09:15:00Z"
        }}}
      ]
    }
  }
}
```

The filter combines exact service/outcome values with a bounded time range. Sorting provides an incident timeline. The result limit bounds returned documents but does not guarantee bounded backend work; selected indices, time scope and query structure still matter. Inspect total-hit interpretation, timeout indicators and shard failures in the response. A partial search result can otherwise be mistaken for a complete absence of events.

Intentionally submit another document with `attempt` as an object to test the schema failure. Inspect the rejection and the pipeline's handling of it. A production shipper must preserve or route rejected records for diagnosis rather than quietly retrying an impossible mapping forever. Cleanup, only after confirming this is your disposable index, uses `DELETE /dispatchdesk-lab-events` in the console. That deletes all documents in this index and is destructive; never replace the name with a broad wildcard.

The query syntax is independent of Ubuntu versus Fedora/RHEL because it runs in the authenticated backend console. Self-hosted server operations still differ in package repositories, filesystem ownership and security policy. Prefer the selected product's supported installation for Ubuntu 24.04, Fedora 44 or RHEL 9, checking support explicitly rather than assuming that one RPM fits every distribution. Keep SELinux/AppArmor enforcement when configuring data directories and service access.

## Managed telemetry and query costs

CloudWatch Logs lets Summit, the fictional managed AWS company, keep logs near its AWS workloads and use service identity and IAM for collection and query access. Managed infrastructure reduces some maintenance work, but Summit still owns log-group boundaries, retention, field contracts, query scope and charges. A forgotten high-volume debug setting can be expensive without any infrastructure failure.

Assume AWS CLI v2 is installed and an existing authorized profile named `dispatchdesk-observer` can read the existing log group `/dispatchdesk/lab/worker` in `eu-central-1`. Replace these names with the actual reviewed account, region and group before execution. The following command starts a **billable query** over existing retained data; it creates no workload infrastructure. Use a role with the necessary Logs query permissions rather than copying application credentials into the terminal.

From an ordinary workstation shell, calculate a fifteen-minute epoch window and launch a query:

```bash
aws sts get-caller-identity --profile dispatchdesk-observer \
  --region eu-central-1 --output json --no-cli-pager || exit 1
```

Inspect the identity result and confirm its Account and Arn match the approved account and observer role before starting billable work. A successful identity lookup establishes identity, not Logs-query permission. Run guarded commands from a dedicated script if you want failure to exit that script rather than your interactive shell.

Only after that identity check, run:

```bash
end_epoch=$(date -u +%s)
start_epoch=$((end_epoch - 900))
query_id=$(aws logs start-query \
  --profile dispatchdesk-observer --region eu-central-1 \
  --log-group-name /dispatchdesk/lab/worker \
  --start-time "$start_epoch" --end-time "$end_epoch" \
  --query-string 'fields @timestamp, event, outcome, order_ref | filter outcome = "provider_timeout" | sort @timestamp asc | limit 20' \
  --query queryId --output text --no-cli-pager) || exit 1
printf '%s\n' "$query_id"
```

The GNU date command is available on the stated Linux baselines; UTC epoch seconds avoid time-zone ambiguity. The arithmetic sets a 900-second window. `--profile` and `--region` select the credential configuration and API region. The log-group argument scopes the data. `--query` is the AWS CLI's response extraction expression, distinct from the Logs Insights query string. Text output captures the ID for subsequent operations; no-cli-pager keeps the shell noninteractive. The failure guard exits this shell procedure if query creation fails; when using an interactive shell, run the guarded block in a dedicated script so failure exits that script. Do not retrieve results without a successfully returned query ID.

Retrieve results using the returned ID:

```bash
aws logs get-query-results \
  --profile dispatchdesk-observer --region eu-central-1 \
  --query-id "$query_id" --output json --no-cli-pager
```

Inspect query status, results and statistics. A running query can have partial results; wait and retrieve again until it completes or fails. To cancel unneeded work, run `aws logs stop-query` with the same profile, region and `--query-id "$query_id"`. Cancellation is an explicit API operation; closing a browser or terminal does not establish that the query stopped. Querying has no generic filesystem cleanup step.

The query assumes JSON event fields were ingested in a discoverable shape. If the application's JSON is nested inside a journal `MESSAGE` string, parse that shape explicitly rather than assuming `outcome` exists at the top level. A query returning no events may indicate the wrong group, time window, region, parser or missing ingestion. IAM denial is another boundary: diagnose access rather than trying broader credentials without review.

Keep group and time scope narrow. A returned-row limit alone need not eliminate scanning cost. Dashboard refreshes can start repeated queries; a twenty-second refresh over a wide incident history can spend money even while nobody is studying the panel. Use aggregate metrics for always-on trend panels and event searches for bounded investigation where appropriate. Consult the actual region's pricing and service quotas during planning; no prices or limits are invented here.

## Choosing a telemetry backend and recovering evidence

Harbor might choose local journals plus modest Loki retention because its small team asks service-scoped incident questions. Summit might choose CloudWatch for AWS integration and managed operations. Atlas might choose a shared searchable event platform where many teams need controlled cross-service analysis. Elastic or OpenSearch can be appropriate when indexed document search is central; Loki can be appropriate when bounded stream selection plus content filtering fits. Compare the required searches, operators available, data sensitivity, retention, export paths and measured ingestion/query demand.

When a search cluster rejects events after a deployment, examine mapping errors and the first changed field. If a timestamp becomes a nested object, changing the dashboard cannot repair ingestion. Stop the incompatible producer or transform the record under a reviewed schema migration. Reindexing historical data consumes storage and compute; preserve source records and verify counts before retiring an old index. A green cluster can still hold an incomplete event history.

For managed ingestion gaps, compare application emission, shipper delivery diagnostics and backend event timestamps. Recover the first failed boundary and determine whether buffered records can backfill before local retention expires. Verify a controlled event end to end. Keep the durable order/notification ledger available for exact reconciliation even when logs were irretrievably lost.

Exercises: distinguish a keyword outcome from a text message; make the strict-mapping failure visible; explain why a twenty-row query can still scan a large history; identify why a completed CloudWatch query with no results does not prove no provider timeouts occurred. Answer guidance: field types preserve different semantics, rejected records need quarantine or correction, scan scope differs from return count, and ingestion/parser/group/time/access boundaries must be checked.

Sources inspected 2026-10-01: [Elastic keyword mapping](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/keyword), [Elastic date mapping](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/date), [Elastic Boolean query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-bool-query), [OpenSearch keyword mapping](https://docs.opensearch.org/latest/mappings/supported-field-types/keyword/), [OpenSearch Search API](https://docs.opensearch.org/latest/api-reference/search-apis/search/), [CloudWatch query syntax](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html), and CLI references for [start](https://docs.aws.amazon.com/cli/latest/reference/logs/start-query.html), [results](https://docs.aws.amazon.com/cli/latest/reference/logs/get-query-results.html) and [stop](https://docs.aws.amazon.com/cli/latest/reference/logs/stop-query.html). An initial Elastic observability page retrieval failed; only the successful sources support claims. No search cluster or AWS query was executed.

