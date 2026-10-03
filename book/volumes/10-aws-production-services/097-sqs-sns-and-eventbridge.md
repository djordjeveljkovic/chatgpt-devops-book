---
book: The Complete DevOps Engineering Book
volume: 10
volume_title: "AWS Production Services"
chapter: 97
title: "SQS, SNS and EventBridge"
slug: sqs-sns-and-eventbridge
status: complete
summary: ../../_ai/chapter-summaries/097-sqs-sns-and-eventbridge.md
---

# Chapter 97 — SQS, SNS and EventBridge

## Queue, fanout and routing semantics

DispatchDesk accepts an order and sends a receipt notification. If the HTTP request synchronously calls an email provider, a slow provider extends the customer response and a provider outage blocks order acceptance. Instead, commit the order and a notification intent in the same database transaction, return an acknowledgment, and let a worker deliver the intent asynchronously. The transactional outbox closes the gap where the database commits an order but the process crashes before publishing a message; the publisher may publish twice, so consumers still need idempotency. See [Chapter 95](095-rds-and-managed-database-operations.md) for database recovery and [Chapter 93](093-ecs-and-fargate-services.md) for service workers.

Amazon SQS is a queue: producers place messages in one queue and competing consumers receive them. It is useful for work distribution, buffering and isolating a producer from worker capacity. A standard queue favors high concurrency but permits duplicate delivery and best-effort ordering. A FIFO queue preserves order within a message group and supports deduplication windows, with throughput and ordering constraints that must match the workload. Neither model makes an external side effect exactly once. If a worker sends an email and crashes before deleting the message, the email can be sent again. Persist a stable intent ID and provider result, use an idempotency facility when the provider offers one, and make duplicate handling explicit. [SQS standard-queue semantics](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html) describe at-least-once delivery; [FIFO delivery logic](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-understanding-logic.html) describes message groups and ordering.

Amazon SNS is pub/sub fanout. A topic can deliver one publication to multiple subscribers, each with its own processing path. For example, an order-created event might feed a notification queue, analytics stream and audit processor. Each subscription has separate delivery behavior and permissions. A queue subscription is often a good fit for a durable worker because it decouples consumer outages from the publisher. Decide whether raw delivery is enabled: without it, an SQS body includes an SNS envelope; with it, the body is the published payload. That choice changes the consumer contract. See AWS's [SNS delivery documentation](https://docs.aws.amazon.com/sns/latest/dg/message-delivery.html).

Amazon EventBridge is an event router. An event bus accepts events and rules route matching events to targets. It is useful when producers and consumers are independently owned or routing depends on event attributes. Prefer a domain event such as `OrderAccepted` with a stable schema and event ID over a command such as “send this exact email now.” EventBridge rules can filter and transform before delivery; an archive can retain selected events for later replay, which is useful for recovery and new consumers but can re-run side effects. [EventBridge concepts](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is-how-it-works-concepts.html) distinguish event buses from point-to-point Pipes and Scheduler.

Choose by delivery shape. Use SQS when workers need competing consumption, backpressure and explicit acknowledgment. Add SNS when one publication should fan out to independent subscribers, commonly with an SQS queue per consumer. Use EventBridge for attribute-based routing across producers and targets, with optional archive/replay. These services can compose, but every hop adds permissions, delivery policy, metrics, retention and failure ownership. A broker does not decide which event is authoritative, whether a side effect is duplicated, or who repairs a poison message.

## Visibility, retries and dead letters

When SQS returns a message, it remains in the queue but is temporarily hidden from other consumers for the visibility timeout. The consumer should delete it only after the durable work succeeds. If it crashes or the timeout expires first, another consumer can receive it. Set the timeout above normal processing duration with room for bounded retries, and extend it for legitimately long work where appropriate. A timeout that is too short increases concurrent duplicate attempts; one that is excessively long delays recovery after a dead worker. SQS visibility is not a lock around an external email or payment system. AWS notes that standard queues can still duplicate delivery during the visibility interval because delivery is at least once. See [visibility timeout guidance](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html).

Use bounded exponential retry with jitter for transient failures and classify permanent failures such as invalid addresses separately. A redrive policy moves a message to a dead-letter queue (DLQ) after a configured receive count. The DLQ is an investigation boundary, not a repair: alert on arrivals, preserve message IDs and trace context, determine whether the root cause is data, code or a dependency, and redrive only after a fix. Redriving at full speed can recreate the original overload. The DLQ must match the source queue type, and its retention policy should allow investigation. For FIFO streams where ordering represents a sequence of state changes, moving one item aside can let later messages progress and break the intended order; decide whether that is acceptable. [SQS DLQ guidance](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html) covers redrive policies and retention behavior.

SNS delivery retries depend on the endpoint protocol. For an SQS subscription, SNS can retry managed-endpoint delivery, but queue consumers still need their own visibility, redrive and idempotency design. For HTTP/S subscribers, configure a subscription DLQ if exhausting delivery retries must not lose an event. EventBridge retries failed target invocations and can send exhausted events to a target DLQ; without one, failed delivery can be dropped. Configure retries and DLQs per target, and test that the DLQ policy permits the service to send messages. An archive is different: it records matching events for replay, while a DLQ records failed delivery to a target. See [SNS retry behavior](https://docs.aws.amazon.com/sns/latest/dg/sns-message-delivery-retries.html) and [EventBridge delivery monitoring](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-monitoring-events-best-practices.html).

## Operating a notification pipeline

Suppose order traffic remains normal, but DispatchDesk notification delay grows from seconds to fifteen minutes. The queue's oldest-message age rises, visible depth climbs and the worker fleet appears healthy. The failed assumption is that running workers imply successful delivery. Inspect provider response classes, worker acknowledgment timing, queue age, in-flight count, receive count and DLQ arrivals. If a provider rate limit is the cause, adding workers increases throttling and retries. Apply a provider-aware concurrency limit, preserve the event, and alert on customer-visible delay rather than CPU alone.

Monitor backlog and age together. A large queue with a fast drain may be acceptable; a small queue whose oldest message is near its retention deadline may be urgent. Track `ApproximateAgeOfOldestMessage`, visible and in-flight counts, empty receives, worker successes/failures and end-to-end notification latency. These queue count metrics are approximate. Add application metrics for accepted intents, delivered outcomes, duplicate suppression and permanent failures. Keep order IDs out of metric labels; use a bounded outcome label and carry a correlation ID in logs or traces under a retention policy.

Estimate worker demand from arrival rate, average service time and desired backlog drain time. If 20 notifications/second arrive, each takes 0.5 seconds of worker time, and the target is to clear a 600-message backlog in 60 seconds while serving new work, capacity must cover both steady arrival work and backlog drain. This is a workload estimate, not an AWS quota or guarantee. Measure tail processing time and provider throttling before setting concurrency. Keep each worker's visibility and shutdown behavior aligned: stop receiving new messages, finish or release in-flight work safely, and avoid deleting a message before its side effect is recorded.

For read-only triage, use AWS CLI v2 from the prepared workstation in [Chapter 82](../09-aws-foundations/082-aws-cli-and-identity-sessions.md), with a profile and region already approved for the account. Inspect queue attributes without receiving or deleting messages:

```bash
set -euo pipefail
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Expected AWS account ID: ' lab_expected_account
read -r -p 'Existing SQS queue URL: ' lab_queue_url
lab_actual_account=$(aws --profile "$lab_profile" --region "$lab_region" \
  --no-cli-pager sts get-caller-identity --query Account --output text)
[[ "$lab_actual_account" == "$lab_expected_account" ]] || {
  printf 'Profile resolved to account %s, not expected account %s\n' \
    "$lab_actual_account" "$lab_expected_account" >&2
  exit 1
}
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  sqs get-queue-attributes --queue-url "$lab_queue_url" \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible \
    ApproximateNumberOfMessagesDelayed VisibilityTimeout MessageRetentionPeriod \
    RedrivePolicy QueueArn --output json
```

This requires `sqs:GetQueueAttributes`; it does not prove consumer health or inspect message contents. Queue URL, ARN and policy may reveal internal topology, so store output in an approved location. Compare the approximate counts with application delivery metrics and CloudWatch age data. Do not use `receive-message` as a casual health check: receiving changes visibility and can interfere with a live consumer.

For replay, establish a bounded time range, target and duplicate-effect plan first. EventBridge archive replay sends matching events back through the event bus; consumers may receive them again. SQS DLQ redrive returns messages to a queue and can increase load. Use a low initial redrive velocity, observe the oldest age and dependency errors, and stop if the repair is not effective. Keep operator identity, incident ticket and replay scope in the audit trail.

## Exercises and answer guidance

1. The email provider accepted a request, then the worker lost its connection before recording success. Should it retry? It must assume the outcome is ambiguous; use a stable intent/idempotency key or reconcile provider state before repeating a non-idempotent side effect.
2. A notification message reaches the DLQ. Is the pipeline repaired? No. Alert, inspect the cause and payload, correct the issue, and redrive with controlled rate only after duplicate and ordering effects are understood.
3. Three consumers need the same `OrderAccepted` event. Should they share one SQS queue? Usually no: competing consumers divide messages. Give each independent consumer its own queue subscription, or choose a routing design that preserves independent delivery.
4. EventBridge replay delivers an event to a new consumer and the email is sent twice. What failed? Replay was treated as harmless; consumer side effects need idempotency and the replay must have an explicit target and duplicate plan.

Review questions: where is intent made durable, what acknowledgment permits deletion, which retries can duplicate work, how are failures retained, and which signal measures user-visible delay?

## Verification and primary sources

AWS SQS standard/FIFO, visibility, DLQ, SNS delivery and EventBridge routing/retry/archive documentation was inspected on 2026-10-04. The AWS CLI example is read-only after account preflight; no queue was queried, created, purged, received from or redriven. No SNS publish, EventBridge replay, worker, email-provider request or cloud configuration was executed. Syntax and static checks do not establish throughput, delivery latency, service quota, endpoint behavior or the application's idempotency.

Primary references: [SQS standard queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html), [FIFO delivery logic](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-understanding-logic.html), [visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html), [dead-letter queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html), [SNS message delivery](https://docs.aws.amazon.com/sns/latest/dg/message-delivery.html), [SNS retries](https://docs.aws.amazon.com/sns/latest/dg/sns-message-delivery-retries.html), [EventBridge concepts](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is-how-it-works-concepts.html), [EventBridge delivery monitoring](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-monitoring-events-best-practices.html), and [EventBridge archive/replay](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-replay-archived-event.html).
