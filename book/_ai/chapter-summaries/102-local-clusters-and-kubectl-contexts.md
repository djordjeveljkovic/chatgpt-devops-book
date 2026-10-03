# Chapter 102 continuation

Status: complete

## Written material
kind/minikube choices and host prerequisites; contexts, kubeconfig merging, namespaces and access; safe explicit-context workflows; wrong-cluster incident; local cleanup cautions; exercises with answer guidance.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
kind, minikube profile, kubeconfig, context, cluster, user, namespace, current-context, local-vs-remote target, client/server version skew.

## Examples and cross-references
Named local cluster creation and read-only context inventory; `kubectl --context` examples; destructive local cluster cleanup is explained but not executed. Builds on Chapter 101 and links Chapter 94 for EKS identity.

## Open threads
None known. Tool versions, driver support, networking, local resources and host security remain environment-specific as described in the chapter.

## Verification
Official Kubernetes, kind and minikube docs inspected 2026-10-04. Scoped validation pending; no cluster was created, deleted or queried.
