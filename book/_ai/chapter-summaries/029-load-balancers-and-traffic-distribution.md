# Chapter 29 continuation

Status: complete

## Written material
Layer 4 and layer 7 balancing; health/readiness contracts and check thresholds; draining and persistence; algorithm choice against work units; annotated loopback HAProxy 3.2-style configuration; uneven traffic diagnosis and exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Transport vs HTTP balancing, TLS termination, target membership, active health check, readiness/liveness, hysteresis, persistence/affinity, drain, request vs connection assignment, weighted/round-robin/least-connections/hash.

## Examples and cross-references
HAProxy fragment binds only to loopback and names two fictional backends and readiness endpoint. Intended for review/config validation with installed release; no listener started. Links to Chapters 24, 28 and 30.

## Open threads
Independent review; HAProxy is not installed, so its configuration was not parsed or deployed. Provider-specific managed balancer behavior not tested.

## Verification
Inspected HAProxy 3.2 configuration manual and current tutorials on algorithms, TCP proxying and health checks on 2026-10-02. Configuration version assumption is explicitly stated; no claim of runtime validation. Link and shell/Python syntax checks are separate evidence.
