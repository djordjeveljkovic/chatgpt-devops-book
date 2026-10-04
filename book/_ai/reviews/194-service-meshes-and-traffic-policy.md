# Independent review — Chapter 194

Reviewer: write_volume7_061_070
Date: 2026-10-04
Reviewed body SHA256: cf8453a4b875b7ca9efa7a497af8d80511fb25018183f915630da1840aded773

## Scope and findings

Reviewed current manuscript and summary, manifest section brief, authoring guide and relevant canonical prerequisite context. Exercises and answer guidance were inspected, relative links checked, and fictional cases distinguished from execution evidence. Summary continuation describes the draft and runtime limits; coordinator should replace pending review/check metadata after this independent review.

Fresh review resolves the initial medium mode-scope finding. The YAML lab now explicitly requires staging sidecar-mode and sidecar-enrolled API/client, and states that selector-based HTTP method/path rules are not ambient examples. Ambient guidance requires waypoint `targetRefs` and separate ztunnel/L4, absent-waypoint, direct Pod-IP and other bypass verification. This matches the official AuthorizationPolicy reference, which requires targetRefs for waypoint policy attachment and ignores selector policies there. The summary accurately includes the repaired scope. No remaining material finding.

Mode tradeoffs, waypoint bypass warning, mTLS versus user authority, resource/retry cost, bounded rollout and prior-policy recovery remain sound. The official CLI reference supports analyze namespace/context flags and local use-kube=false. No CLI binary or cluster enforcement run occurred.

## Primary verification 2026-10-04

- [https://istio.io/latest/docs/reference/config/security/authorization-policy/](https://istio.io/latest/docs/reference/config/security/authorization-policy/)
- [https://istio.io/latest/docs/reference/config/security/peer_authentication/](https://istio.io/latest/docs/reference/config/security/peer_authentication/)
- [https://istio.io/latest/docs/ambient/usage/waypoint/](https://istio.io/latest/docs/ambient/usage/waypoint/)
- [https://istio.io/latest/docs/reference/commands/istioctl/#istioctl-analyze](https://istio.io/latest/docs/reference/commands/istioctl/#istioctl-analyze)

## Validation and limits

Initial Volume 20 checker passed all ten drafts. Fresh `python3 tools/check_book.py --chapters 194-194` checked one draft chapter, 2 shell syntax blocks, 1 YAML parse and 1,514 global local links. Chapter 194 has no finding; the global link scan reported one out-of-scope broken link from Chapter 202 to the currently absent Chapter 204. No warnings. This concurrent Volume 21 issue does not invalidate Chapter 194 prose approval and must be resolved before global promotion validation. Renderer and SQLite teaching labs were independently run as described above for Chapters 192–193; temporary files were removed. No Kubernetes server admission/deployment, Istio analysis/enforcement, provider resource, restricted network, migration, billing account, production architecture or incident action was exercised. Syntax parsing does not establish API schema, policy enforcement or service recovery.

Verdict: approved
