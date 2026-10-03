# Independent review — Chapter 107

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 8dcb1f1b9d616288e6ea55e6c223788ea25d518383f44000cb1a7b798aae9c4e

## Findings

No unresolved findings. Current body now qualifies liveness termination/restartPolicy, preStop grace extension and minReadySeconds availability. All prior low findings are resolved; approval remains appropriate.

## Scope and dated primary evidence

Read the complete current body and summary, SKELETON brief and previously read authoring guide; independently refreshed Chapter 106 prerequisite and previously reviewed Chapters 103–105 lifecycle/controller/endpoint material. All ordered brief topics are covered, with concrete probe-driven restart failure, diagnosis, source-of-truth recovery and answer-guided exercises. Summary correctly states teaching-fragment/nonexecution scope; not every chapter-number mention is a clickable link.

Retrieved official documentation on 2026-10-04: [probe concepts](https://kubernetes.io/docs/concepts/workloads/pods/probes/), [probe configuration task](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/), [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/), [sidecar containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/) and [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/). The official lifecycle-hook source was retrieved in Chapter 103's same-date review and remains applicable.

Startup gates readiness/liveness until success; readiness failure does not itself restart; configured consecutive failure thresholds, usual periods and individual timeouts are described correctly. Startup 24 times 5 seconds is roughly a two-minute check budget, explicitly not measured startup duration. HTTP named port resolves to 8080; default probes target Pod IP, and TCP/exec/gRPC distinctions and resource/failure assumptions are sound. YAML apps/v1 Deployment selector matches labels, probes have valid positive values and named port, Pod grace 45 seconds and image reference is clearly unpullable until replaced. It is explicitly an excerpt requiring implemented endpoints, not a production-ready contract; no apply is instructed.

Normal preStop-before-stop-signal flow and shared grace accounting, SIGTERM default qualification, forced termination, asynchronous endpoint convergence, existing-connection overlap and terminating endpoint conditions are coherent. No guarantee of zero interrupted requests or deterministic sidecar ordering is asserted. Restart-loop reasoning properly separates shared dependencies from unrecoverable local progress and requires measured/staged recovery. Read-only kubectl blocks explicitly pin kind-dispatchdesk/production; label inventory can include other components but named Pod replacement is explained. rollout status has a bounded observation timeout. No distro-specific installation/unit/security changes occur; prepared Ubuntu/Fedora/RHEL clients use identical API syntax. No fabricated measured output appears.

## Validation and limits

`python tools/check_book.py --chapters 106-108` on 2026-10-04 checked three draft chapters, five YAML blocks, four shell blocks and 1,356 global links. It reported four global missing-Chapter-109 links from PROGRESS, SKELETON, volume README and Chapter 103; no warnings or chapter-local errors for 106–108. This is not an overall pass. Earlier missing-Chapter-108 links are resolved. No runtime/cluster operation occurred; prior execution limits remain. Only review records changed. Whole-file hash matches the supplied value.

Verdict: approved
