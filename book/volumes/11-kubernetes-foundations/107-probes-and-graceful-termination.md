---
book: The Complete DevOps Engineering Book
volume: 11
volume_title: "Kubernetes Foundations"
chapter: 107
title: "Probes and Graceful Termination"
slug: probes-and-graceful-termination
status: complete
summary: ../../_ai/chapter-summaries/107-probes-and-graceful-termination.md
---

# Chapter 107 — Probes and Graceful Termination

## Startup, readiness and liveness

A process can exist without being ready to accept work, and a process that once became ready can later stop making progress. Kubernetes probes let the kubelet ask a container about different parts of that lifecycle. A startup probe answers whether startup has completed. A readiness probe answers whether this instance should receive ordinary Service traffic. A liveness probe answers whether the process is so stuck that restarting the container is a reasonable recovery. These signals have distinct consequences; using one endpoint for all three without understanding those consequences can turn a slow dependency into a restart storm.

A failed readiness probe marks the container and Pod as not ready, but it does not restart the container. A Service normally excludes not-ready Pods from its usable backends, giving the application time to recover while other replicas continue serving. A failed liveness probe causes the affected container to be stopped after the configured consecutive failure threshold; whether it starts again depends on the Pod's `restartPolicy` (Deployments use `Always`). A startup probe delays both readiness and liveness checks until it succeeds, which protects a slow but viable startup sequence from an overly aggressive liveness policy. If no probe is configured, Kubernetes does not infer application health from an open port or a running process.

The following Deployment excerpt configures all three probes for the Chapter 104 DispatchDesk API:

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
      app.kubernetes.io/name: dispatchdesk
      app.kubernetes.io/component: api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: dispatchdesk
        app.kubernetes.io/component: api
    spec:
      terminationGracePeriodSeconds: 45
      containers:
        - name: api
          image: registry.example.invalid/dispatchdesk/api@sha256:REPLACE_WITH_VERIFIED_DIGEST
          ports:
            - name: http
              containerPort: 8080
          startupProbe:
            httpGet:
              path: /health/startup
              port: http
            periodSeconds: 5
            timeoutSeconds: 2
            failureThreshold: 24
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            periodSeconds: 5
            timeoutSeconds: 2
            failureThreshold: 2
            successThreshold: 1
          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            periodSeconds: 10
            timeoutSeconds: 2
            failureThreshold: 3
```

This is a teaching manifest: replace the image placeholder with a verified artifact digest, and implement each endpoint with the semantics described below. The named port resolves to container port 8080. The startup threshold gives roughly two minutes of failed checks after the probe begins before the kubelet restarts the container; it is a budget, not a promise that startup takes two minutes. A successful startup probe ends that startup window and enables the other probes. `periodSeconds` controls the usual interval, `timeoutSeconds` bounds an individual check, and `failureThreshold` controls consecutive failures before the action applies. Defaults and interactions are versioned API behavior; use the [probe reference](https://kubernetes.io/docs/concepts/workloads/pods/probes/) for the cluster's supported release.

The startup endpoint should report success when initialization required before service begins has completed. The readiness endpoint should report success only when this instance can safely accept the requests routed to it. It may account for local initialization and capacity, but should not blindly fail every replica because an optional dependency has a short outage. A liveness endpoint should be cheap and focused on process progress, such as a deadlock that cannot self-recover. If liveness depends on every downstream service, a shared database or network outage can cause all replicas to restart together, adding load during the failure. Kubernetes cautions that poor liveness checks can create cascading failures.

HTTP probes run against the Pod IP and configured port; the application must listen on that address and return a success status for a healthy check. Other handlers include TCP socket checks, exec commands inside the container and, where supported, gRPC health checks. TCP success proves only that a socket accepts a connection. An exec probe can test local state but consumes container resources and may fail if its command is missing. HTTP and TCP probe configuration is not application-level traffic from a remote user; authentication, virtual-host routing and proxy behavior can differ. Avoid an endpoint that performs an expensive diagnostic on every probe interval.

Readiness is not a replacement for application observability. A Pod can be ready while returning incorrect data, and a readiness check can itself be broken. Pair the signal with request metrics, errors, latency, logs and synthetic/user-facing checks. During rollout, readiness controls when a Pod counts as available for the Deployment after any configured `minReadySeconds` stability period and influences Service endpoint eligibility. It does not guarantee that every client has discarded cached endpoints or that all existing connections have moved. [Chapter 105](105-services-and-cluster-dns.md) explains the Service and EndpointSlice path.

## Termination and traffic draining

When a Pod is deleted or its controller replaces it, Kubernetes records the deletion and a grace period. The kubelet runs any `preStop` hook, then asks the container runtime to stop the process, normally by sending SIGTERM. The application must handle that signal: stop accepting new work, finish or safely abort in-flight requests, flush bounded local state, close connections and exit before the grace period expires. Processes that do not stop in time can be forcibly killed. The common default Pod grace period is 30 seconds, but it should be chosen from measured shutdown needs and the surrounding traffic and dependency behavior.

The grace-period clock includes time spent in `preStop`. A hook that sleeps for 20 seconds inside a nominal 30-second budget leaves about 10 seconds for signal handling and exit, though kubelet behavior can include a small one-off extension if the hook is still running at expiry. Treat the configured value as an operational budget, not an exact wall-clock guarantee. Hook handlers can fail and delivery is intended to be at least once, so make them lightweight and safe to repeat. A sleep-only hook is not a reliable substitute for application shutdown: it consumes the same finite budget and does not itself stop accepting requests. The application should perform its shutdown work in response to the termination signal. See [container lifecycle hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/) and [Pod termination](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/).

At the same time, Kubernetes updates endpoint information for a terminating Pod. EndpointSlices identify terminating endpoints and their readiness/serving conditions so traffic-management components can react. Readiness and endpoint propagation are asynchronous relative to process shutdown; do not assume that a Service stops sending all traffic before SIGTERM reaches the app. The application should tolerate a short overlap: a request may arrive during endpoint convergence, and clients with an existing keep-alive connection may continue to use it. A robust server stops accepting new connections on shutdown and finishes existing requests within a bounded drain window.

The Deployment strategy and grace period interact. A rolling update can start replacements while old Pods terminate, so capacity must account for overlap. `maxUnavailable: 0` does not mean no old requests are interrupted; availability is a control-plane accounting signal, not a transaction guarantee. If a long-running request takes two minutes but the grace period is 45 seconds, it will not be preserved simply because the Pod was Ready before deletion. Set timeouts across the request chain so an upstream request deadline, server drain, process shutdown and Pod grace period fit together. Preserve idempotency or checkpoints for work that cannot finish before shutdown.

To inspect a rollout and termination evidence in the disposable cluster, use explicit context and namespace:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  get pods -l app.kubernetes.io/name=dispatchdesk -o wide
kubectl --context kind-dispatchdesk --namespace production \
  describe pod POD_NAME
kubectl --context kind-dispatchdesk --namespace production \
  get endpointslices -l kubernetes.io/service-name=dispatchdesk-api -o yaml
kubectl --context kind-dispatchdesk --namespace production \
  rollout status deployment/dispatchdesk-api --timeout=120s
```

Replace `POD_NAME` with a Pod name from the first read. These commands inspect state and may expose application metadata in terminal history or logs; do not dump Secret values. Look at readiness conditions, probe events, restart counts, termination timestamps, endpoint conditions, and the Deployment's available replicas. No expected output is asserted because these commands were not run.

## Preventing probe-driven restart loops

Suppose a Deployment rollout begins, but all three API Pods restart repeatedly while the database is slow. Events show liveness failures. The initial assumption was that a failing database connection means the API process is irrecoverably stuck. Yet the process is still making progress, and restarting every replica creates new connection attempts and removes capacity. The recovery is to stop the harmful restart policy through the reviewed Deployment source, inspect startup and readiness separately, and determine whether the database dependency should make an instance unready or whether a bounded liveness check should detect only an unrecoverable local failure.

A common mistake is to set `initialDelaySeconds` to a guessed startup time and then use liveness as a startup gate. Delays become inaccurate as caches, migrations, hardware or traffic change. Prefer a startup probe for legitimately slow initialization, with a failure budget based on measured worst-case startup plus margin. While startup has not succeeded, liveness and readiness probes do not run. Once it succeeds, readiness can control traffic admission and liveness can detect later deadlock. If startup exceeds its budget, the container is restarted; inspect logs and events before simply increasing the threshold, because the process may be failing for a deterministic reason.

Probe thresholds must fit observed behavior. A `timeoutSeconds` of one can be too short during CPU contention; a high `failureThreshold` delays recovery from a real deadlock. A readiness probe that flaps can repeatedly remove and re-add replicas, concentrating load on remaining Pods. A too-permissive check can route requests to a broken instance. Measure check latency and application recovery, test dependency failures, and make the response reflect the decision the control plane will take. For a container whose work should complete once, such as a Job, liveness restarts can also change retry behavior; choose probes and restart policy according to the workload's completion contract.

When diagnosing repeated restarts, first determine which probe failed and which container restarted. `kubectl describe pod` events often distinguish startup, readiness and liveness failures. Compare `restartCount`, current and previous logs, exit status, CPU/memory pressure, node health, and application dependency metrics. A readiness failure by itself should not increment restarts. If only one replica fails, compare its node, configuration and recent template; if every replica fails together, look for a shared endpoint, overloaded dependency or faulty probe rollout. Roll back the probe change through the Deployment when it caused the incident, then introduce a measured policy with a staged rollout.

Graceful shutdown has its own failure modes. If requests fail at the end of a rollout, check whether the server handles SIGTERM, whether its PID 1 process receives the signal, whether a wrapper script forwards signals, whether `preStop` consumes too much time, and whether the configured timeout budget covers real in-flight requests. Inspect logs and traces around termination. If a sidecar is present, account for its own lifecycle and the cluster version's sidecar semantics; do not assume arbitrary container shutdown order in a regular multi-container Pod. The safest policy is to make each container tolerate concurrent shutdown unless a Kubernetes-native sidecar feature explicitly defines ordering for the supported cluster.

## Exercises and answer guidance

1. A Pod's process runs, but it has not finished loading its model. Which probe should prevent traffic before initialization completes? A startup probe can gate startup checks; readiness must remain false until the model is loaded and the instance can serve.
2. The database is briefly unavailable, but the API can queue bounded work and recover. Should liveness fail on every database error? Usually not. Readiness may be appropriate if requests cannot be served, while liveness should detect unrecoverable process failure rather than a shared dependency outage.
3. A `preStop` hook takes 25 seconds and the Pod grace period is 30 seconds. How much normal shutdown budget remains? At most about five seconds, less any additional shutdown overhead; the grace period includes the hook.
4. Liveness passes, readiness fails, and the container has not restarted. Is that expected? Yes. Readiness removes the Pod from ordinary Service backend selection while leaving the process running for recovery.
5. A request lasts longer than the Pod grace period during a rollout. Does readiness guarantee it will finish? No. The server needs a bounded drain policy and timeout compatibility, or the work must be retryable/checkpointed.

Review questions: what decision does each probe control, how does a startup probe gate the other probes, which steps consume the termination grace period, and what evidence distinguishes an unhealthy process from an unhealthy dependency?

## Verification and primary sources

Official Kubernetes probe, lifecycle-hook, Pod termination, sidecar and Pod lifecycle documentation was inspected on 2026-10-04. The Deployment fragment is illustrative; its health endpoints and shutdown handling must exist in the application. No cluster commands, rollout, probe failure, HTTP request or termination event were executed. Static checks do not establish probe thresholds, request draining, signal forwarding, endpoint convergence, application recovery or sidecar compatibility for a live cluster.

Primary references: [probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/), [probe configuration task](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/), [container lifecycle hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/), [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/), and [sidecar containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/).
