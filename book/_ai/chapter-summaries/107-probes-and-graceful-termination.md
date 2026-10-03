# Chapter 107 continuation

Status: complete

## Written material
Startup/readiness/liveness differences and probe budgets; traffic drain, grace-period accounting and signals; restart-loop diagnosis and recovery; exercises with answer guidance.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
startupProbe, readinessProbe, livenessProbe, failureThreshold, endpoint conditions, SIGTERM, preStop, terminationGracePeriodSeconds, request draining.

## Examples and cross-references
DispatchDesk Deployment health-probe excerpt and read-only rollout/endpoint diagnosis, assuming `kind-dispatchdesk` and `production`; links to Chapters 104–106. No cluster operation executed.

## Open threads
None known. Probe thresholds and termination timing require validation against the target cluster and application as described in the chapter.

## Verification
Official Kubernetes probe, lifecycle, sidecar and Pod termination docs inspected 2026-10-04. No live probe, request drain or rollout tested.
