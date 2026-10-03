# Chapter 110 continuation

Status: complete

## Written material
Object identity/spec/status and controllers; `get`, `describe`, `logs`, `exec`, events, label and field selectors; scoped incident diagnosis with evidence and recovery; exercises with answer guidance.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
UID, namespace, spec/status, owner reference, label selector, field selector, event retention, previous container logs, ephemeral debug container.

## Examples and cross-references
Read-only DispatchDesk diagnostics assume `kind-dispatchdesk`/`production`; targeted output/redaction warnings; direct links to Chapters 102, 103, 104, 105, 107 and 109. No API reads or mutations executed.

## Open threads
None known. Live state, RBAC, event/log retention and sensitive output remain environment-specific as described in the chapter.

## Verification
Official Kubernetes object, selector, kubectl and Pod debug docs inspected 2026-10-04. No cluster interaction performed.
