---
book: The Complete DevOps Engineering Book
volume: 11
volume_title: "Kubernetes Foundations"
chapter: 110
title: "kubectl Diagnostics and API Objects"
slug: kubectl-diagnostics-and-api-objects
status: complete
summary: ../../_ai/chapter-summaries/110-kubectl-diagnostics-and-api-objects.md
---

# Chapter 110 — kubectl Diagnostics and API Objects

## `get`, `describe`, `logs`, `exec` and events

Kubernetes incidents are easier to diagnose when each command answers one question. `get` lists object state, `describe` combines selected configuration and related events, `logs` shows output emitted by a container process, and `exec` runs a command inside a live container. Events add time-bounded evidence about scheduling, image pulls, probes, mounts and controller actions. None of these views alone proves an application is healthy. Build a timeline and follow references from a symptom to the object and controller responsible for it.

Every object has a kind, name, namespace when namespaced, UID and current API version. Names identify an object of a given kind within its scope; UIDs identify object instances across deletion/recreation. Most objects have a desired `spec` and a system-populated `status`. Controllers compare desired and observed state and act to close the gap. For example, a Deployment spec may request three replicas while status reports one available replica. The difference is diagnostic evidence, not necessarily a broken API server. The [Kubernetes object model](https://kubernetes.io/docs/concepts/overview/working-with-objects/) and [owners/dependents](https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/) explain those fields and relationships.

Start by pinning the intended context and namespace in every command. These read-only examples assume the disposable [`kind-dispatchdesk` context from Chapter 102](102-local-clusters-and-kubectl-contexts.md), `production` namespace, and [Chapter 104's Deployment](104-deployments-replicasets-and-jobs.md):

```bash
kubectl --context kind-dispatchdesk --namespace production \
  get deployment dispatchdesk-api
kubectl --context kind-dispatchdesk --namespace production \
  get pods -l app.kubernetes.io/name=dispatchdesk,app.kubernetes.io/component=api -o wide
kubectl --context kind-dispatchdesk --namespace production \
  get service dispatchdesk-api
kubectl --context kind-dispatchdesk --namespace production \
  get endpointslices -l kubernetes.io/service-name=dispatchdesk-api
kubectl --context kind-dispatchdesk --namespace production \
  describe deployment dispatchdesk-api
kubectl --context kind-dispatchdesk --namespace production \
  get events --sort-by=.lastTimestamp
```

The first command compares desired and available counts. The Pod query selects both labels because comma-separated selector requirements are ANDed; `-o wide` adds placement and IP columns. The Service query reads the named API object, and the EndpointSlice query uses its standard service-name label. `describe` shows a human-oriented view including related objects and events. Events are a useful recent timeline but are subject to retention and may not explain an old failure. Do not infer that a missing event means an action never happened.

For a specific Pod, `describe` gives conditions, per-container state, restart counts, image, volume mounts and recent events. `kubectl --context kind-dispatchdesk --namespace production get pod POD_NAME -o yaml` exposes the full API representation, which can reveal fields omitted from a summary table. It can also include configuration references and sensitive metadata; do not paste full output into a public ticket or incident chat without review. Never retrieve or decode Secret data as a routine debugging step. When a Pod is managed by a Deployment, inspect the Deployment and ReplicaSet as well as the Pod: the controller's template is the source of desired state, and a Pod may be replaced at any time.

Container logs are separate from Kubernetes Events. Select a container explicitly when a Pod has more than one:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  logs POD_NAME -c api --tail=100 --timestamps
kubectl --context kind-dispatchdesk --namespace production \
  logs POD_NAME -c api --previous --tail=100 --timestamps
```

Replace `POD_NAME` with the affected Pod from `get`. The first command reads recent output from the current container; the second requests the prior terminated container's logs when available. Runtime rotation, container restarts and log-driver policy can limit history. Logs may contain credentials or customer data, so restrict access, preserve only what policy allows, and redact before sharing. Use labels to narrow candidate Pods, then inspect individual replicas when their behavior differs; aggregated logs can obscure which instance emitted a line.

`exec` is useful for checking the environment or process from inside a running container, but the target image may not contain a shell or diagnostic utilities. The command below is a read-only example only if the container has `/bin/sh` and `printenv`:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  exec POD_NAME -c api -- printenv LOG_LEVEL
kubectl --context kind-dispatchdesk --namespace production \
  exec POD_NAME -c api -- /bin/sh -c 'id; ls -la /etc/dispatchdesk'
```

The command after `--` runs in the container. Do not dump all environment variables: they may include credentials. `exec` does not work if the container is stopped, and a distroless image may lack a shell. Adding an ephemeral debug container is a separate API mutation requiring permission and may change the Pod's debug metadata; use it only under the incident procedure. A local shell inside a container also cannot prove the same network policy, identity or request path as a remote client. See [Debug Running Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/) for additional methods.

Event API objects are namespaced, including Events that refer to cluster-scoped Nodes. Query a namespaced Pod's Events in its namespace; querying Node-related Events across namespaces requires permission to list Events across those namespaces. For example, use `kubectl --context kind-dispatchdesk --all-namespaces get events --field-selector involvedObject.kind=Node,involvedObject.name=NODE_NAME` and replace `NODE_NAME` with the affected node. Field-selector requirements are ANDed, and Event supports selectors for involved-object fields. Filter by involved object where useful, and correlate timestamps with the Pod's current/previous state and application logs. Event messages are best-effort operational signals, not a durable audit log. Their content may vary by Kubernetes and controller version. For durable history, use an approved event export or observability system.

## Object fields, labels and selectors

Labels are key/value metadata intended to group and select objects. A label does not prove ownership or uniqueness: multiple Pods can share a label, and a Deployment controller tracks ReplicaSets through owner references in addition to selectors. A label selector such as `app.kubernetes.io/name=dispatchdesk,app.kubernetes.io/component=api` requires both constraints. Set-based selectors support `in` and `notin`; existence and nonexistence use a bare key such as `partition` or `!partition`. There is no general OR between separate requirements. Field selectors filter supported object fields, such as `status.phase=Pending`, but supported fields vary by resource type.

The following read commands show how label and field selectors answer different questions:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  get pods -l 'app.kubernetes.io/name=dispatchdesk,app.kubernetes.io/component=api' \
  -L app.kubernetes.io/version
kubectl --context kind-dispatchdesk --namespace production \
  get pods --field-selector=status.phase=Pending -o wide
kubectl --context kind-dispatchdesk --namespace production \
  get replicasets -o wide
```

The label query chooses a workload group and adds a version label column if present; the field selector filters by Pod phase. Neither is a substitute for inspecting controller ownership, readiness conditions or application health. Consult the supported field-selector list for the resource being queried. Labels can be changed, so diagnose the actual values on the objects rather than assuming a manifest was applied exactly as intended. See [labels and selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) and [field selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/field-selectors/).

`-o wide` is good for a quick view; `-o yaml` or `-o json` exposes full fields for careful inspection. JSONPath and custom columns can focus on one value, but a successful query only means the API returned that field. A displayed Pod `Running` phase does not mean it is Ready; inspect conditions and container states. An empty EndpointSlice set, a mismatch between Service selector and Pod labels, or a Pod with `Ready=False` provides different evidence and points to different repair steps. [Chapter 103](103-pods-and-application-lifecycles.md), [Chapter 105](105-services-and-cluster-dns.md) and [Chapter 107](107-probes-and-graceful-termination.md) explain those lifecycle and traffic concepts; [Chapter 109](109-persistent-volumes-and-stateful-workloads.md) covers storage-specific diagnostics.

Avoid broad commands such as `kubectl get all` as a complete inventory. The `all` shorthand includes a subset of common resources, not every resource kind, and does not necessarily show related objects such as PVCs, Secrets, ConfigMaps, custom resources or EndpointSlices. Use explicit resource kinds based on the failing path. Similarly, a cluster-wide query with `--all-namespaces` can disclose metadata across teams; limit scope unless broader access is needed and authorized.

## A first Kubernetes incident investigation

Assume DispatchDesk returns intermittent 503 responses. A colleague says “Kubernetes is down” because one Pod shows `Running`. Start from the affected request and scope: which client, namespace, Service, time window and release version? Then follow the control-plane path without making changes. Check Deployment availability and Pod readiness; compare labels with the Service selector; inspect every EndpointSlice and its endpoint conditions; review probe and scheduler events; and inspect current and previous logs for the affected container. Chapter 105's network checks help distinguish DNS, endpoint and application-listener failures.

If one Pod has repeated readiness failures after a new release while other replicas are Ready, capture its description, events, current/previous logs, version labels and owner references. Compare its spec and node with a healthy replica. A failed readiness check should normally remove the Pod from Service backend use without restarting it; if restart counts increase, inspect liveness/startup failures, process exits and node pressure instead. If all replicas become unready together, examine shared dependencies, configuration rollout and network policy rather than deleting every Pod.

Recovery follows the owning object and the evidence. If the new Deployment revision introduced an invalid readiness path, the service owner can use the approved source of truth or a scoped rollout undo, then wait for the Deployment to converge and verify real requests from the client path. A rollback changes a Pod template; it cannot undo schema changes or customer effects. If only one Pod has a node-specific mount failure, replacing it blindly may move the same failure or risk state; consult the storage diagnosis in Chapter 109. Do not patch a generated Pod, delete a PVC, print Secrets, or restart the whole namespace as a first reaction. Record what was observed, the exact change made, its scope and the post-change evidence.

During an incident, capture a small set of reproducible facts: command and target context, namespace, object name/UID, timestamp, relevant spec/status fields, event messages, and redacted log excerpts. Keep the original timeline and note which outputs are observations versus hypotheses. Kubernetes API objects are continuously reconciled, so an object can change between commands. If a diagnosis depends on one field staying stable, retrieve related objects close together or use the monitoring system's time series for historical evidence.

## Exercises and answer guidance

1. A Pod is `Running` but the Service has no usable endpoints. Which fields or objects should be inspected? Pod Ready condition, readiness-probe events, Service selector, live Pod labels and EndpointSlice conditions.
2. `kubectl logs POD` shows no useful output after a crash. What should be tried? Select the correct container and use `--previous` if the prior container instance's logs remain available; then inspect termination state and events.
3. A Deployment has three desired replicas but one available. Should the generated Pod be edited to fix its probe? No. Inspect the owning Deployment/ReplicaSet and change the reviewed template through its source of truth.
4. Does `kubectl get all -A` show every resource in a cluster? No. It is a shorthand for a subset of common types; query relevant PVCs, config, endpoints and custom resources explicitly.
5. A colleague posts full `kubectl get pod -o yaml` output containing Secret values or customer data. What should happen? Remove or restrict the exposed data according to incident policy, rotate compromised credentials as needed, and share a redacted focused field set.

Review questions: which diagnostic question does each of `get`, `describe`, `logs` and `exec` answer, how do labels differ from owner references, why are Events not a durable audit source, and how should an investigation distinguish observation from hypothesis?

## Verification and primary sources

Official Kubernetes object, label/selector, field-selector, kubectl describe/logs and debug-running-Pod documentation was inspected on 2026-10-04. Commands are illustrative and explicitly target the local `kind-dispatchdesk` context and `production` namespace. No API read, log retrieval, exec, debug-container mutation, rollout or incident recovery was performed. Static checks do not establish live object state, access permissions, event retention, log availability, application correctness or confidentiality of a cluster's output.

Primary references: [Kubernetes objects](https://kubernetes.io/docs/concepts/overview/working-with-objects/), [labels and selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/), [field selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/field-selectors/), [kubectl describe](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_describe/), [kubectl logs](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/), and [Debug Running Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/).
