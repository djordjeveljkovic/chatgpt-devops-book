---
book: The Complete DevOps Engineering Book
volume: 22
volume_title: "Operational Reference"
chapter: 214
title: "Kubernetes Command and Object Reference"
slug: kubernetes-command-and-object-reference
status: complete
summary: ../../_ai/chapter-summaries/214-kubernetes-command-and-object-reference.md
---

# Chapter 214 — Kubernetes Command and Object Reference

Kubernetes diagnosis begins with an object, its controller and an observed symptom. This reference connects those observations to commands without repeating the reconciliation model from [Volume 11](../11-kubernetes-foundations/README.md) or production design from [Volume 12](../12-kubernetes-production-engineering/README.md). A running Pod, a successful rollout and a healthy order journey are different claims.

Examples require a configured kubectl client compatible with the target cluster, a known context and appropriate credentials. The cluster may be local, self-managed or managed by a provider; those choices change operational ownership even when the command is identical. Run observations from an authorized workstation, not by installing unrestricted cluster credentials on every application node.

## Confirm the target before observing or changing it

```bash
kubectl config get-contexts
kubectl config current-context
book_context='dispatchdesk-lab'
book_namespace='dispatchdesk'
kubectl --context "$book_context" get namespace "$book_namespace"
kubectl --context "$book_context" --namespace "$book_namespace" auth can-i get pods
```

Replace the two example names with verified entries. `get-contexts` lists local configuration, while `current-context` reports its current selection. Neither proves that a server is reachable. The explicit `--context` on subsequent commands prevents dependence on a later default-context change. `get namespace` performs a server observation; it can fail because of reachability, authentication, authorization or absence of the named resource. `auth can-i` asks whether the identity is authorized for the specified action and resource; authorization is not a promise that the operation will succeed under every admission or resource condition.

Keep context and namespace visible in incident notes. Do not post a complete kubeconfig, which can contain credential material. Some authentication plugins refresh credentials by invoking an external program; a seemingly read-only client operation can therefore depend on a separate identity service. [Local Clusters and kubectl Contexts](../11-kubernetes-foundations/102-local-clusters-and-kubectl-contexts.md) explains setup and version compatibility. The [current-context reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_config/kubectl_config_current-context/) documents the local selection command.

## Inspect the objects that own the symptom

Use the explicit context on every command below. Short resource names such as `pods`, `deployments` and `services` address different API objects, not interchangeable views of one process.

```bash
kubectl --context "$book_context" --namespace "$book_namespace" get deployments,pods,services -o wide
kubectl --context "$book_context" --namespace "$book_namespace" get pods -l app=dispatchdesk-api -o yaml
kubectl --context "$book_context" --namespace "$book_namespace" describe deployment dispatchdesk-api
kubectl --context "$book_context" --namespace "$book_namespace" get events --sort-by=.metadata.creationTimestamp
```

`-o wide` adds selected human-readable fields; its columns depend on resource type. `-l` selects objects whose labels match the expression. `-o yaml` returns their API representation, including observed status, rather than the exact original source file. `describe` assembles explanatory information and related events. Events are time-limited diagnostic hints, not a durable complete audit trail. Sorting the currently available events by creation time makes a sequence easier to inspect but cannot reconstruct events already expired or aggregated away. The [get reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_get/) describes selection and output forms.

| Object or condition | Useful observation | What it does not prove |
|---|---|---|
| Deployment | Desired replicas, available replicas, generation and rollout conditions | That a database migration is compatible or a notification is delivered |
| ReplicaSet | Owner reference and Pods belonging to a rollout | That manually changing it is the correct desired-state repair |
| Pod | Phase, container states, restart counts, readiness and scheduling conditions | That `Running` means every container is ready or customer traffic succeeds |
| Job/CronJob | Completion, failure and schedule history | Exactly-once external effects or absence of duplicate jobs |
| Service | Selector, ports and type | That its selected backends are ready or reachable through every network path |
| EndpointSlice | Backend addresses, ports and conditions | That a remote client traverses the full traffic path successfully |
| PVC/PV | Binding, storage class, access mode and events | That application data is consistent or backed up |
| Node | Conditions, allocatable capacity and placement constraints | That spare host memory can satisfy any Pod or storage topology |

Follow owner references upward when an object keeps returning after deletion. The repair usually belongs to the controller's desired state. Deleting a Pod created by a Deployment triggers replacement; it does not permanently reduce replicas. See [Deployments, ReplicaSets and Jobs](../11-kubernetes-foundations/104-deployments-replicasets-and-jobs.md).

## Logs, execution and temporary access

For a known Pod called `dispatchdesk-api-abc123`, inspect the relevant container explicitly:

```bash
kubectl --context "$book_context" --namespace "$book_namespace" logs dispatchdesk-api-abc123 -c api --since=15m --timestamps
kubectl --context "$book_context" --namespace "$book_namespace" logs dispatchdesk-api-abc123 -c api --previous
kubectl --context "$book_context" --namespace "$book_namespace" exec dispatchdesk-api-abc123 -c api -- printenv LOG_LEVEL
```

`-c api` selects a container. `--since=15m` bounds recent log output and `--timestamps` adds timestamps. `--previous` asks for the prior terminated instance of that container when its logs are still available; it does not recover every historical restart. The [logs reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/) defines these options. Central retention belongs to the observability system, not the assumption that a replaced Pod preserves its old files.

`exec` starts a command inside the selected running container; the `--` separates kubectl's arguments from the program's arguments. Even a diagnostic execution consumes resources and may reveal sensitive data. The example reads one non-secret variable rather than dumping the entire environment. Minimal images may lack a shell or `printenv`; the resulting error is not proof that the application failed. A controlled debug-container procedure can help, but its extra tools, privilege and lifetime require the cluster's policy and a verified compatible image.

For a temporary loopback tunnel to a known Service:

```bash
kubectl --context "$book_context" --namespace "$book_namespace" port-forward service/dispatchdesk-api 18080:8080 --address=127.0.0.1
```

The left port is on the workstation; the right port identifies the Service-side port mapping. Leave the process running in a separate terminal and stop it with Ctrl-C when done. This path bypasses the normal public gateway and can fail when the selected backend is replaced. A successful request through the tunnel helps isolate backend behavior, but does not validate public DNS, TLS, gateway policy or normal client reachability. Verify the actual Service port before copying the mapping.

## Review and apply a desired-state change

Assume `./deployment.yaml` is a reviewed, complete manifest targeting the intended workload. These are change-preparation commands:

```bash
kubectl --context "$book_context" --namespace "$book_namespace" apply --dry-run=server -f ./deployment.yaml
kubectl --context "$book_context" --namespace "$book_namespace" diff -f ./deployment.yaml
```

`-f` supplies the local file. Server dry-run asks the API server to process the request without persisting the proposed resource, subject to supported admission behavior and authorization. It is stronger schema/admission evidence than parsing YAML locally, but does not schedule a real Pod or prove startup. `diff` compares the proposed configuration with current state; a reported difference normally produces exit status 1, while a command failure uses a different failure status. Build automation must distinguish expected differences from an inability to compare.

After review, `kubectl ... apply -f ./deployment.yaml` changes desired state. With `--server-side --field-manager=dispatchdesk-release`, server-side apply assigns an explicit field-management identity; conflicts need an ownership decision, not routine `--force-conflicts`. The [apply reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/) documents both execution modes. GitOps-managed objects should usually change through their source of truth; an imperative edit may be overwritten by reconciliation.

Observe the release rather than inferring completion from the apply response:

```bash
kubectl --context "$book_context" --namespace "$book_namespace" rollout status deployment/dispatchdesk-api --timeout=120s
kubectl --context "$book_context" --namespace "$book_namespace" rollout history deployment/dispatchdesk-api
```

`--timeout` bounds how long the client waits, not how long the cluster may continue reconciliation. By default, rollout status follows the latest rollout; a concurrent deployment can change which revision is being observed. Pin a known revision with `--revision` when that distinction matters. The [rollout-status reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_status/) describes this behavior. A timeout is a reason to inspect Pods, events and readiness evidence, not automatically to delete the Deployment.

`rollout undo deployment/dispatchdesk-api` changes the workload to a recorded earlier template. It cannot reverse an incompatible database migration, restore deleted objects, or guarantee that an old image remains available. Check retained history and compatibility before using it. A GitOps controller can restore its still-new desired template unless the source is corrected. [Rollback, Roll Forward and Release Incidents](../14-delivery-deployment-and-gitops/140-rollback-roll-forward-and-release-incidents.md) supplies the recovery contract.

## Match common symptoms to the next observation

| Symptom | Investigate next | Avoid this unsupported inference |
|---|---|---|
| Pod remains Pending | Scheduling events, requests, taints, topology and PVC state | That buying another node fixes every placement constraint |
| ImagePullBackOff | Exact image reference, registry access, pull secret and platform | That an application-code restart changes registry permissions |
| CrashLoopBackOff | Current/previous logs, exit reason, configuration and startup policy | That repeated deletion repairs the startup cause |
| OOMKilled | Memory limit, working set, allocation growth and workload | That all host memory was exhausted |
| Service has no useful responses | Selector, EndpointSlices, readiness, ports and network path | That the Service object itself launches application instances |
| Deployment stalls | Available capacity, rollout strategy, probe failures and old/new replicas | That apply success means customer availability |

These are decision routes, not diagnoses established by the symptom alone. A Service error can involve a selector mismatch, a wrong target port or a healthy backend isolated by policy. Preserve the tested path and identity when comparing evidence from inside and outside the cluster.

Review drill: a Deployment reports two replicas, one Pod is Pending, and public requests fail intermittently. Determine available rather than merely desired capacity; inspect the Pending reason, ready endpoints and the rollout's headroom. Resolve the actual scheduling or readiness condition, then test a known order and verify asynchronous work. Do not treat a dashboard's replica count as an availability guarantee.

## Verification and limits

The linked official generated command references were inspected on 2026-10-01 for context, get, logs, apply and rollout behavior. Examples name fictional objects and expected diagnostic actions. No kubectl executable or cluster was available in the authoring environment; no API requests, Pod execution, apply, rollout or rollback were run. Local shell syntax and link checks are distinct from live Kubernetes or schema validation. Independent technical review remains pending.
