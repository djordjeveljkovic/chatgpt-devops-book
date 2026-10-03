---
book: The Complete DevOps Engineering Book
volume: 11
volume_title: "Kubernetes Foundations"
chapter: 101
title: "Kubernetes Architecture and Reconciliation"
slug: kubernetes-architecture-and-reconciliation
status: complete
summary: ../../_ai/chapter-summaries/101-kubernetes-architecture-and-reconciliation.md
---

# Chapter 101 — Kubernetes Architecture and Reconciliation

## API server, controllers and etcd

Kubernetes is a system for declaring and continuously managing objects, not a remote shell that runs a command once and forgets it. The cluster stores records such as Deployments, Pods, Services and Nodes. Their `spec` describes requested configuration; their `status` reports what the system currently observes. Controllers act on differences between those views. A ReplicaSet maintains the number of matching Pods and creates replacements from its template when a Pod is missing. It does not generally reconcile every field of an existing Pod back to that template, so a manual child-object edit may persist until that Pod is replaced. Durable workload changes belong in the parent object and its source of truth.

A cluster has a control plane and worker nodes. The `kube-apiserver` exposes the Kubernetes API over HTTPS. `kubectl`, controllers, schedulers, operators and other clients communicate with the API server; they do not normally edit etcd directly. The server authenticates and authorizes requests, applies admission checks and validation, and persists accepted objects to etcd. The API server is the front door for both declarative configuration and observed status. In a high-availability cluster, multiple API server instances can be placed behind a stable endpoint. [Kubernetes cluster architecture](https://kubernetes.io/docs/concepts/architecture/) describes the components and their separation.

etcd is the consistent key-value store used by Kubernetes for cluster state. It is not a user-facing application database, and workload teams should not treat it as an interface for custom reads or writes. A cluster depends on the health, capacity, access control and backup/recovery of this store. Managed Kubernetes services operate some or all of this control-plane layer, but the workload owner still needs an application recovery plan. A successful `kubectl apply` means the API accepted a change; it does not prove the application became ready or that the prior state can be restored.

The `kube-scheduler` watches for Pods that have not been assigned to a node. It selects a suitable node using resource requests, node constraints, affinity, taints and other scheduling inputs, then records the binding through the API. Scheduling is a placement decision. It does not pull the image, start the process, make the application healthy or guarantee that the Pod can reach a database. Those steps involve node and workload components.

The `kube-controller-manager` runs built-in controllers, each responsible for part of the API's behavior. The Deployment controller manages ReplicaSets; a ReplicaSet manages a requested number of matching Pods; the Job controller creates Pods for finite work; endpoint controllers maintain Service backends from eligible Pods. A controller commonly watches one resource and creates or updates another through the API. Each controller observes again after acting, so interruptions are expected to be retried. Controllers generally aim to move the cluster toward a desired state, not execute a single exact sequence of commands. See the Kubernetes [controller pattern](https://kubernetes.io/docs/concepts/architecture/controller/).

Some controllers also communicate with systems outside Kubernetes. A cloud controller may create a cloud load balancer or route; a storage controller may provision a volume; a cluster autoscaler may request a node. These integrations introduce credentials, quotas, API availability and cost beyond the Kubernetes API. The request can be accepted and remain pending while an external dependency fails. Identify which controller owns each object transition before debugging it.

## Nodes, kubelet and container runtime

A Node object represents a worker machine known to the cluster. The kubelet runs on that machine and reports node and Pod status to the API server. It receives Pod specifications, asks the container runtime to create and manage containers, and reports what is running. The kubelet is an agent, not the scheduler: it executes the Pod assigned to its node but does not choose where that Pod belongs. Node capacity and conditions in the API are observations used by controllers and the scheduler. A stale or unhealthy Node object can therefore affect placement even when a VM appears powered on.

The container runtime implements the Container Runtime Interface (CRI) used by kubelet. Common runtimes include containerd and CRI-O. The runtime pulls images, prepares containers and runs their processes, while Kubernetes deals in Pods and higher-level API objects. This boundary is why `kubectl get pods` can show `ImagePullBackOff` or `CrashLoopBackOff` without telling the whole host-level story. Logs, Pod events, kubelet/runtime evidence and registry access may each explain a different part of a failure. For OCI image and runtime details, see [Chapter 46](../05-container-internals-and-oci/046-oci-runtimes-and-container-engines.md).

The node also needs networking and storage integrations. A CNI plugin provides Pod networking; Service routing is implemented by kube-proxy or a compatible networking implementation; CSI drivers connect Pods to storage systems. These components may be installed and operated by a cluster distribution or cloud provider. A Pod can be scheduled but fail before becoming Ready because its network plugin cannot allocate an address, a volume cannot attach, an image cannot be fetched, or an init container cannot complete. A `Running` Pod phase alone is not a guarantee that the application is ready to receive traffic.

The API presents desired and observed state; the node runs processes. If the API server is temporarily unavailable, containers already running on a node may continue, but new changes cannot be reliably accepted and controllers cannot coordinate normal reconciliation through the API. If a worker loses control-plane connectivity, its workloads may continue for a time while status and control actions are delayed. Exact behavior depends on the component, runtime and failure duration. Do not equate “control plane unreachable” with an immediate process stop, or assume existing processes will remain healthy indefinitely.

## Following a desired-state change

DispatchDesk wants three API replicas during a busy period. A version-controlled Deployment might declare the key intent like this:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dispatchdesk-api
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dispatchdesk-api
  template:
    metadata:
      labels:
        app: dispatchdesk-api
    spec:
      containers:
        - name: api
          image: registry.example.invalid/dispatchdesk/api@sha256:REPLACE_WITH_VERIFIED_DIGEST
          resources:
            requests:
              cpu: 500m
              memory: 512Mi
```

The image reference is intentionally a placeholder, not a pullable image. In a real repository, replace the full placeholder with an approved immutable image digest whose repository and digest were verified; do not merely change the text after `@sha256:`. Include the complete application configuration, probes, security settings and rollout strategy; later chapters build these details. The selector must match the Pod template labels. Applying such a manifest is a write to the selected cluster and namespace. It should happen through the team's reviewed deployment process, not as an unexplained command pasted into an incident transcript.

The reconciliation path is a chain, not one action. First, the API server validates and stores the Deployment. The Deployment controller observes the new specification and creates or updates a ReplicaSet. That ReplicaSet controller creates Pod objects until the desired count is represented. The scheduler watches each unassigned Pod, checks placement constraints and resource requests, and binds it to a node. The kubelet on that node sees the Pod assignment, asks its runtime to pull the image and start containers, and publishes status. Readiness checks and other controllers then influence whether the Pod is considered ready for service endpoints. Controllers continue observing state and correcting drift. Kubernetes documents objects as records of intent and explains [desired spec versus observed status](https://kubernetes.io/docs/concepts/overview/working-with-objects/).

This process is asynchronous. API acceptance is not readiness. The status update may lag, an image pull may be slow, scheduling may fail, or admission can reject the object before persistence. A healthy controller loop works toward convergence, but it cannot manufacture node capacity, valid credentials, free IP addresses or healthy dependencies. If multiple controllers are involved, each makes progress based on its own inputs and permissions. A system may remain in a changing intermediate state while it retries.

Suppose DispatchDesk asks for three replicas but only two become ready. The application owner assumed that increasing replicas automatically creates compute capacity. A read-only triage from an authorized workstation starts by verifying which cluster and namespace the current context selects:

```bash
kubectl config current-context
kubectl cluster-info
kubectl get nodes -o wide
kubectl get deployment dispatchdesk-api -n production
kubectl get replicasets -n production -l app=dispatchdesk-api
kubectl get pods -n production -l app=dispatchdesk-api -o wide
```

Then describe the Pending Pod and inspect recent namespaced events:

```bash
kubectl describe pod POD_NAME -n production
kubectl get events -n production --sort-by=.metadata.creationTimestamp
```

Replace `POD_NAME` with the actual Pending Pod name found in the preceding output. These commands read cluster state; they do not change the workload. Confirm the context, cluster endpoint and namespace before any later write. The Deployment view compares desired, updated, available and ready replica counts; the ReplicaSet and Pod views show whether child objects exist and where they are placed. `describe` includes event and scheduling details. Event history is finite and may age out, so collect it promptly alongside controller, scheduler, kubelet, runtime and application logs where permitted.

For a concrete failure, assume this Deployment's Pending Pod requests 500 millicores while every remaining eligible node has less than that amount of unallocated schedulable CPU. Its Pod event may show `FailedScheduling` and insufficient CPU; the Kubernetes [Pod debugging guide](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/) describes this evidence pattern. Treat event messages as diagnostic clues, not as a substitute for checking node allocatable capacity, existing requests, affinity, taints and actual workload needs. If the request is wrong, correct the reviewed Deployment source and roll out a realistic request. If it is correct, add or resize capacity through the cluster's approved node-management process, then watch the scheduler bind the Pod and kubelet report readiness. Do not lower requests simply to make the Pod schedule if doing so would overcommit the service. Deleting the Pending Pod only causes its ReplicaSet to create another Pod from the same template, with the same unsatisfied constraints.

Reconciliation also explains why editing a child object can appear ineffective. If an operator deletes one of the three Pods, the ReplicaSet notices that only two remain and creates a replacement from its template. If an operator edits a generated Pod's image directly, that edit may persist on that Pod; the ReplicaSet does not generally copy the template field back onto an existing child or trigger a rollout. Other replicas remain unchanged, so the workload can temporarily run mixed images. A later Pod replacement will use the template image. The durable correction belongs in the parent object or its source of truth, such as a reviewed manifest or GitOps repository. Conversely, if a human imperatively changes the live Deployment while a GitOps controller continues applying an older repository version, the two controllers can continually overwrite one another. Choose one management path per object and resolve drift in that path.

Reconciliation is a mechanism, not a business policy. It cannot determine whether three replicas are enough for a traffic spike, whether requests are sized from measurements, whether a readiness probe checks the right dependency, or whether the deployment is safe for users. Operators choose those desired values and design signals that distinguish healthy progress from a persistent stall. For a small team, Kubernetes can provide useful scheduling, restart and rollout behavior, but it also adds API, networking, storage and upgrade responsibilities. Compare that ongoing work with a managed container service or a simpler host before adopting it; see [Chapter 94](../10-aws-production-services/094-eks-and-aws-integration.md) for the EKS operational boundary.

## Exercises and answer guidance

1. The API accepted a Deployment with three replicas. Does that prove three application instances can serve traffic? No. Inspect ReplicaSet/Pod creation, scheduling, kubelet startup, readiness and the Service's eligible endpoints.
2. A Pod is Pending because no node satisfies its CPU request and node selector. Should the operator delete the Pod? No. Its controller recreates it. Correct the reviewed request/placement policy or add suitable capacity, then observe scheduling.
3. An operator changes one generated Pod's image, but the Deployment still declares the old image. Must the ReplicaSet immediately revert that Pod? No. The edit may persist on that Pod and create a mixed-version workload; replacement Pods come from the template. Change the Deployment/source of truth and observe its rollout rather than assuming child fields are continuously reconciled.
4. `kubectl` cannot reach the API server, but an existing process still answers requests. Is that impossible? No. Data-plane processes may continue while control-plane observation and desired-state changes are unavailable; inspect both paths and follow the cluster runbook.

Review questions: where is desired state stored, which component acts on each transition, what evidence distinguishes scheduling from startup failure, and where should an operational correction be recorded?

## Verification and primary sources

Kubernetes architecture, object, controller, node and Pod-debugging documentation was inspected on 2026-10-04. The kubectl examples are read-only, but were not executed against a cluster. The manifest is illustrative and contains a placeholder image; no object was applied, scaled, patched or deleted. No node, container runtime, API server, etcd, network plugin, storage driver or controller was exercised. Static review does not establish cluster-specific reconciliation timing, capacity, permissions, readiness, runtime health or recovery behavior.

Primary references: [cluster architecture](https://kubernetes.io/docs/concepts/architecture/), [nodes](https://kubernetes.io/docs/concepts/architecture/nodes/), [controllers](https://kubernetes.io/docs/concepts/architecture/controller/), [Kubernetes objects and spec/status](https://kubernetes.io/docs/concepts/overview/working-with-objects/), [kubectl API interaction](https://kubernetes.io/docs/concepts/overview/kubectl/), and [debugging Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/).
