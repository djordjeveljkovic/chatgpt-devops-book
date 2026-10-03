# Chapter 98 continuation

Status: complete

## Written material
Lambda lifecycle and invocation differences; concurrency budgeting; SQS batch partial failure and idempotency; ZIP/container packaging; operational metrics; Lambda versus ECS/Fargate decision; timeout and rollout reasoning; exercises with answers.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Execution environment, cold/warm start, synchronous/asynchronous invoke, event-source mapping, reserved/provisioned concurrency, partial batch response, idempotency, alias/version rollout.

## Examples and cross-references
DispatchDesk SQS notification handler pseudocode and provider-throttle scenario; links to Chapters 93 and 97. No code or AWS operation executed.

## Open threads
Review required. Runtime support, concurrency quotas, timeouts and provider/database budgets are environment-specific.

## Verification
AWS primary docs inspected 2026-10-04. Scoped checker still required. Pseudocode is illustrative; no runtime, load, invocation or deployment test performed.
