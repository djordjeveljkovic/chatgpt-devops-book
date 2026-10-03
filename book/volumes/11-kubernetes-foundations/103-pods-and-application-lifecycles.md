---
book: The Complete DevOps Engineering Book
volume: 11
volume_title: "Kubernetes Foundations"
chapter: 103
title: "Pods and Application Lifecycles"
slug: pods-and-application-lifecycles
status: complete
summary: ../../_ai/chapter-summaries/103-pods-and-application-lifecycles.md
---

# Chapter 103 — Pods and Application Lifecycles

## Pod identity and container restart

A Pod is the smallest Kubernetes object that is scheduled as a unit. It groups one or more containers that share a network identity and can share volumes. Containers in the same Pod are placed together on one Node; they are not separate replicas or independent scaling units. Most application Pods contain one main container. Add a second container when it has a tightly coupled lifecycle and shared local communication or files, not merely because two processes are part of the same product.

Pods are replaceable units, not durable virtual machines. A Pod receives a unique UID and node assignment. If a workload controller replaces it, the new Pod is a different object even if it receives a similar name and runs the same image. Local writable container layers and `emptyDir` storage belong to the Pod/node lifecycle and are not a durable database. Put durable state in a suitable external system or PersistentVolume, and design the application to recover from a new Pod starting with no local state. See [Chapter 109](109-persistent-volumes-and-stateful-workloads.md) for persistent data.

Kubernetes reports a Pod `phase` such as `Pending`, `Running`, `Succeeded`, `Failed` or `Unknown`. A phase is a high-level summary, not a complete health state machine. A Pod can be `Running` while its container repeatedly crashes, while the app is not ready, or while requests fail. `kubectl` also displays helpful `STATUS` strings such as `CrashLoopBackOff`; that display value is not itself the Pod phase. Inspect conditions, per-container state, restart count, exit code, events and logs. The official [Pod lifecycle reference](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) explains the distinction.

The kubelet starts a container through the container runtime and tracks its `Waiting`, `Running` or `Terminated` state. A Waiting container may be pulling an image, applying configuration or waiting on another startup step. A Terminated container has an exit reason and code; if the Pod restart policy permits it, kubelet may start a new container instance inside that same Pod on the same node. This is different from a controller creating a replacement Pod after the Pod is deleted or a node is lost. Container restart does not rerun a new Deployment rollout, and restarting a process cannot repair bad configuration or missing downstream capacity.

For ordinary application Pods managed by a Deployment, the default `restartPolicy` is `Always`: a container process that exits is restarted, regardless of whether it exited successfully. Standalone Pods and Jobs have different reasons to choose other policies; a Job normally wants completion rather than endless process restart. Repeated failures enter exponential backoff, visible as `CrashLoopBackOff`, to avoid tight restart loops. The backoff state says that attempts are delayed; it does not tell you whether the process failed because of a bad command, missing secret, failed dependency, permission problem or resource exhaustion. Use `kubectl logs POD -c CONTAINER --previous` to inspect the last terminated container when it has restarted, and `kubectl describe pod` for state and event context.

## Init containers and lifecycle hooks

Regular init containers run before application containers and complete in the order declared. They can perform bounded setup such as validating a mounted configuration file, rendering a local config from inputs, or waiting for a dependency that is expected to become available. If an init container fails, kubelet retries it according to the Pod restart policy; the Pod does not become ready until initialization succeeds. A failed init container can therefore keep every main container from starting. Inspect `.status.initContainerStatuses`, events and init-container logs rather than debugging an application process that has not started.

Use init containers for work that is safe to repeat and belongs to that Pod's startup contract. Do not use them as a substitute for a migration controller that must run exactly once across a fleet. Three replicas can all run the same init step, and a restarted Pod runs init containers again. A database schema change must be backward-compatible with the old and new application versions or be orchestrated separately with idempotency and ownership. Likewise, a startup script that waits forever for an unavailable dependency can make the failure less visible instead of recovering it.

Kubernetes supports `postStart` and `preStop` container lifecycle hooks. `postStart` is triggered when the container is created, concurrently with its entrypoint; there is no guarantee the hook runs before application code. If initialization ordering matters, put it in the application or an init container with explicit sequencing. A slow or failed hook can delay or restart the container. Hook delivery may be retried, so handlers should be idempotent and safe to run more than once. See [container lifecycle hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/).

When Kubernetes terminates a container, it first runs `preStop` if configured, then asks the runtime to send the process its stop signal. The Pod termination grace period is a shared time budget that includes the hook and the process's shutdown. A hook that consumes nearly all of that budget leaves the application little time to finish requests; when the grace period expires, termination can be forced. The default grace period is commonly 30 seconds, but applications should set a value based on measured shutdown needs and the surrounding rollout/load-balancer behavior. Do not rely on `preStop` as the only graceful shutdown mechanism: the process itself should handle its stop signal, stop accepting work, finish or safely abandon in-flight requests, and exit before the deadline. Chapter 107 develops probes and termination in detail.

A Kubernetes sidecar is a specialized long-running supporting container associated with a Pod, such as a local proxy or log processor. Current Kubernetes supports restartable init-container sidecars, but support depends on cluster version and feature availability. Avoid depending on this newer form without verifying the cluster version; ordinary multi-container Pods have existed longer but do not guarantee an arbitrary startup/shutdown order among app containers. Keep shared fate and resource use in view: one container's memory/CPU pressure, readiness or lifecycle can affect the Pod as a whole.

## Deploying and inspecting a small service

To observe the Pod lifecycle, use a disposable local cluster from [Chapter 102](102-local-clusters-and-kubectl-contexts.md). The following manifest runs the Kubernetes project's small `agnhost` test server, which listens on port 8080. It is a learning/test image, not a production application. The tag comes from the current Kubernetes tutorial; for a controlled repeatable build, resolve and pin the approved digest for the image rather than assuming a tag never changes.

Save this as `pod.yaml` in an empty lab directory:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: dispatchdesk-netexec
  labels:
    app: dispatchdesk-netexec
spec:
  restartPolicy: Always
  containers:
    - name: server
      image: registry.k8s.io/e2e-test-images/agnhost:2.53
      command: ["/agnhost"]
      args: ["netexec", "--http-port=8080"]
      ports:
        - name: http
          containerPort: 8080
          protocol: TCP
```

This standalone Pod is suitable for observing container state and a simple HTTP process. It creates one Pod and consumes local cluster resources. From a terminal configured for the named local context `kind-dispatchdesk`, apply and inspect it:

```bash
kubectl --context kind-dispatchdesk --namespace default apply -f pod.yaml
kubectl --context kind-dispatchdesk --namespace default get pod dispatchdesk-netexec -o wide
kubectl --context kind-dispatchdesk --namespace default describe pod dispatchdesk-netexec
kubectl --context kind-dispatchdesk --namespace default logs dispatchdesk-netexec -c server
```

`apply` changes the selected cluster; only use this in the disposable local lab. The other commands inspect the Pod, including node, phase, conditions, container state, restart count and recent events. To test the server without defining a Kubernetes Service yet, port-forward its port to a local port in one terminal and send an HTTP request from another:

```bash
kubectl --context kind-dispatchdesk --namespace default port-forward pod/dispatchdesk-netexec 18080:8080
```

```bash
curl --fail --show-error http://127.0.0.1:18080/hostname
```

Port-forwarding is a local diagnostic tunnel, not a production exposure method. The response should identify the Pod host name; no particular output is asserted here because the command was not run. Stop the foreground port-forward with Ctrl-C. Remove the test Pod when finished:

```bash
kubectl --context kind-dispatchdesk --namespace default delete pod dispatchdesk-netexec
```

Deletion is a state change and permanently removes the standalone Pod's API record and ephemeral data. In this lab it is expected cleanup; do not delete production Pods as a first diagnostic step.

Now consider two startup failures. If a separate Pod definition has an init container that never exits, its status may show `Init:0/1`; inspect the init container state and logs because the main server has not begun. If the server shows `CrashLoopBackOff`, run `kubectl logs --previous` for that container and inspect its last exit code and events. If phase is `Running` but the HTTP check fails, verify the process arguments, listening port and logs; `containerPort` is descriptive metadata and does not make a process listen on that port. A port-forward can connect only if the process is actually listening. A future Service requires a selector and endpoints, which Chapter 105 covers.

## Exercises and answer guidance

1. A Pod is `Running` but reports `0/1` Ready. Does Running mean it can receive traffic? No. Phase and readiness are different signals; inspect container state and later the Pod conditions/probe behavior.
2. A container exits with code 0 in a Deployment Pod, and then starts again. Why? The default Pod restart policy is `Always`; a successful process exit still causes the container to restart in the same Pod.
3. An init container is stuck waiting for a database that is unavailable. Should the application container be debugged first? No. It has not started. Inspect init status/events/logs and decide whether the dependency belongs in the startup contract or needs a different orchestration path.
4. A preStop script takes 25 seconds and the Pod has a 30-second grace period. How much time remains for normal process shutdown? At most about five seconds, before accounting for other timing; the hook consumes the shared termination budget.
5. `containerPort: 8080` is present but port-forward receives connection refused. What does that field prove? Only the declared port metadata; verify the process command and actual listening socket.

Review questions: which state belongs to the Pod versus container, what restarts a process versus creates a replacement Pod, what work is safe to repeat during initialization, and how is shutdown time budgeted?

## Verification and primary sources

Kubernetes Pod lifecycle, init-container, hook, phase and probe documentation was inspected on 2026-10-04. The `agnhost` test image and server command are sourced from the Kubernetes tutorial. The manifest and commands are examples only and were not executed. No cluster or Pod was created, queried, port-forwarded or deleted. Static checks do not establish image availability, server behavior, runtime compatibility, startup timing, hook delivery, graceful shutdown or live application readiness.

Primary references: [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/), [init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/), [container lifecycle hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/), [Kubernetes test server tutorial](https://kubernetes.io/docs/tutorials/hello-minikube/), and [probe configuration](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).
