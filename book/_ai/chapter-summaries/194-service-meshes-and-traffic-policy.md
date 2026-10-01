# Chapter194 continuation

Status: draft

## Written material
Requirement-to-mesh capability table, sidecar/ambient ownership/failure matrix, full scoped PeerAuthentication and AuthorizationPolicy example, read-only CLI analysis and staging change path, bypass/security nuance, ordered symptom table, rollout/recovery, resource/latency/retry and exercises.

## Exact next section
Independent Istio-version/API/identity-policy review and manifest parse.

## Concepts and terminology
Workload mTLS versus user/tenant authorization; sidecar versus node tunnel/optional waypoint; L4/L7; proxy selection versus API persistence; policy denial versus business outcome.

## Examples and cross-references
DispatchDesk staging API/client principal, named trust-domain assumption, bounded GET/POST methods; Harbor/Summit/Atlas economics and ownership; crosslinks191,193,198 and canonical Kubernetes/security/operations.

## Open threads
Istio workload migration/analysis/policy and cluster checks unexecuted. Validate exact `istioctl analyze` invocation and whether analysis path uses `--namespace` as stated; CLI not locally available. Existing policy ownership must be audited in reader staging cluster.

## Verification
Istio1.31 current documentation and Kubernetes primary references inspected2026-10-01. Checker/YAML parser pending. No installation or cluster mutation.
