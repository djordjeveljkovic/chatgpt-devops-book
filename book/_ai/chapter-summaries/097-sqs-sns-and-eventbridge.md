# Chapter 97 continuation

Status: complete

## Written material
Queue versus pub/sub versus event routing; standard/FIFO delivery; idempotent consumers; visibility, retries and DLQs; EventBridge archives/replay; notification backlog diagnosis; read-only queue inspection; exercises with answers.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
SQS, SNS, EventBridge, transactional outbox, at-least-once delivery, FIFO message group, visibility timeout, redrive policy, DLQ, event archive/replay, approximate backlog metrics.

## Examples and cross-references
DispatchDesk order notification pipeline and a read-only SQS queue-attribute command with account preflight; links to Chapters 82, 93 and 95. No cloud operation executed.

## Open threads
Review required. Provider idempotency, queue dimensions, quotas, target delivery and runtime capacity need environment-specific validation.

## Verification
AWS primary service docs inspected 2026-10-04. Scoped checker and shell syntax validation still required; no AWS calls, delivery tests, replay or redrive performed.
