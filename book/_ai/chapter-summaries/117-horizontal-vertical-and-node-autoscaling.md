# Chapter 117 continuation

Status: complete

## Written material
HPA, VPA and node autoscaler responsibilities and interaction; metrics and resource requests; scale-up/down tradeoffs; scheduler and provider limits; DispatchDesk demand and capacity incident; read-only diagnostics and exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
HPA, VPA, node autoscaling, resource metrics, custom/external metrics, requests, limits, pending Pods, scale-to-capacity delay.

## Examples and cross-references
DispatchDesk API peak with HPA bounds, DB connection saturation and unschedulable Pods; read-only HPA/Pod/node inspection; links to Chapters 116 and 114.

## Open threads
Verify current autoscaler implementation and metric adapter behavior in the target cluster; no live test performed.

## Verification
Scoped checker and local-link validation pending; official Kubernetes autoscaling docs inspected 2026-10-04.
