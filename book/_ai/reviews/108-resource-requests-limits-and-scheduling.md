# Independent review — Chapter 108

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 3c49ba3b481a17fc6d301026194c1e8749a5594ecc1dd886efe572303602fb31

## Findings

No unresolved findings. Fresh re-review of corrected passages and links: Prior technical/defaulting/accounting fixes and correct Chapter 117 reference remain sound. Direct prerequisite links and the summary Chapter 117 reference are now accurate.

## Scope and dated primary evidence

Read full Chapter 108, its summary and SKELETON brief, previously read authoring guide, and refreshed prerequisite Chapter 107. Prior Chapter 104 request/rollout and Chapter 102 context material establish dependencies. All brief topics and exercises/answer guidance are covered; fictional measurements are labeled, and recovery uses reviewed canary/resource changes rather than indiscriminate constraint deletion. Summary accurately states nonexecution; not every chapter-number reference is a clickable body link.

Retrieved official sources on 2026-10-04: [resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/), [node-pressure eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/), [QoS](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/), [kubectl top pod](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_top/kubectl_top_pod/) and [HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/). The resource reference explicitly documents copying a specified limit into an absent request, CPU quota enforcement, reactive memory OOM and ephemeral-storage measurement/enforcement. Eviction documentation supports usage-relative-to-request and priority ranking rather than absolute QoS protection. QoS description is valid for the familiar per-container API; newer Pod-level/sidecar accounting is qualified rather than prescribed. HPA CPU utilization relative to request makes the doubled-request exercise sound.

The illustrated three 500m/512Mi replicas account for 1.5 CPU/1536Mi before additional Pod/container/host overhead; limit 1 CPU/768Mi is coherent and labeled illustrative. Scheduler request accounting, allocatable versus capacity, placement constraints, OOM versus node-pressure eviction and measured right-sizing are generally accurate. Limits are not automatic dedicated CPU allocation or physical memory reservation. Read-only kubectl commands consistently target kind-dispatchdesk/production, explain POD_NAME and previous lastState termination, and require Metrics Server/compatible resource API for top. top is correctly described as a sample without throttling/history evidence. JSONPath syntax emits termination reasons/newline; no full Secret data is requested. Events sorted by lastTimestamp are valid but timestamp population/retention can vary. No distro-specific host installation/security changes occur, so prepared Ubuntu/Fedora/RHEL clients use the same commands.

## Validation and limits

`python tools/check_book.py --chapters 108-110` passed on 2026-10-04: three draft chapters, three YAML checks, six shell blocks and 1,370 global local links; no errors/warnings. Previous missing110 global-link issue is resolved. Syntax/parsing does not prove API schema/admission or runtime semantics. No runtime/cluster operations occurred; previous documented execution limitations remain. Fresh whole-file hash matches the latest supplied value. Protocol body hash above binds this approval to current prose. Only separate review records changed.

Verdict: approved
