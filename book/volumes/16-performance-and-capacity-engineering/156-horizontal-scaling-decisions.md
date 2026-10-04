---
book: The Complete DevOps Engineering Book
volume: 16
volume_title: "Performance and Capacity Engineering"
chapter: 156
title: "Horizontal Scaling Decisions"
slug: horizontal-scaling-decisions
status: complete
summary: ../../_ai/chapter-summaries/156-horizontal-scaling-decisions.md
---

# Chapter 156 — Horizontal Scaling Decisions

**Section outline:** replace instance-local state with explicit ownership; quantify the shared-resource replica budget; choose coordination semantics; separate startup, readiness and draining; add replicas in a controlled experiment.

## Replicas change the ownership of work

Horizontal scaling adds independently scheduled execution units. They may be processes on one VPS, separate virtual machines, ECS tasks, or Kubernetes pods. Two processes on one host can improve CPU use without protecting against host failure. Two machines in one failure domain can survive a process fault without surviving that domain's outage. Replicas provide the intended benefit only when placement, routing and state ownership match the requirement.

[Vertical scaling](155-vertical-scaling-decisions.md) gave Harbor a way to relieve a measured resource constraint while keeping operations simple. Summit chooses an ECS service and managed database because its workload is bursty and its small operations team wants less host management. Atlas uses Kubernetes because many teams require runtime isolation and a platform contract. These are distinct choices. None makes application coordination disappear.

DispatchDesk acknowledges an order only after durable order state and notification intent exist. A replica cannot keep that state only in its own Python dictionary, PHP session directory, Go map or Node.js heap. A load balancer can route the next request elsewhere; a restart can erase it entirely. The deliberately in-memory API from [Chapter 141](../15-observability-and-telemetry/141-observability-from-questions-to-evidence.md) teaches instrumentation and remains unsuitable for this production acceptance contract. “Stateless API” means a replaceable process whose important state is elsewhere or can be reconstructed. It does not mean the product has no state.

List state before adding replicas: durable orders, idempotency records, notification intent, session or authentication state, cached catalog data, configuration, upload objects, temporary files and in-flight requests. Give each a persistence requirement and owner. A temporary decoded payload may safely disappear with a failed request. An acknowledged order may not. A local cache can be rebuilt, but two replicas must agree about freshness expectations. Sticky routing can hide a local-state defect during normal operation and then reveal it during failover.

## The shared bottleneck sets the useful replica count

Suppose a controlled staging experiment shows one API replica handles eight eligible attempts per second within the latency target while the database has ample reserve. Three equivalent replicas might support twenty-four attempts per second under balanced traffic. That is a hypothesis, not a guarantee. A database lock or external provider limit can flatten aggregate throughput long before the third replica reaches its CPU ceiling.

For a concrete budget, let the database allow 180 connections for this service after reserving space for administration and other workloads. Each API replica has a pool maximum of twenty; four worker replicas each have ten. Six API replicas imply 160 possible connections. Eight imply 200, exceeding the budget before a deployment surge adds temporary processes. Counting the steady-state replicas only is insufficient. Idle pool connections also consume slots even when CPU demand is low.

Store the assumptions in this complete `replica_budget.py` file. Run it with Python3 as an ordinary user on Ubuntu, Fedora or RHEL. This is a local arithmetic exercise; it does not create services or inspect a live database.

```python
import math

peak_attempts_per_second = 36
validated_rate_per_api = 8
usable_fraction = 0.75
database_connection_budget = 180
api_pool_max = 20
worker_replicas = 4
worker_pool_max = 10
rolling_surge = 1

api_needed = math.ceil(peak_attempts_per_second /
                       (validated_rate_per_api * usable_fraction))
steady_connections = (api_needed * api_pool_max +
                      worker_replicas * worker_pool_max)
rollout_connections = steady_connections + rolling_surge * api_pool_max
print(f"modeled API replicas: {api_needed}")
print(f"maximum steady connections: {steady_connections}")
print(f"maximum rollout connections: {rollout_connections}")
if rollout_connections > database_connection_budget:
    raise SystemExit("Plan exceeds the database connection budget")
print("Connection arithmetic fits; performance and failures still need testing")
```

```bash
python3 replica_budget.py
```

The seventy-five-percent fraction is a chosen reserve in this fictional plan, not a universal target. The model asks for six API replicas and includes one additional replica during rollout. A passing arithmetic check proves only consistency of these inputs. Pool behavior, query demand, worker traffic, connection churn and uneven request costs still need measurement. If the check fails after changing inputs, evaluate smaller pools, a different rollout policy, reduced work or a database capacity change before raising the replica ceiling.

## Coordination mechanisms have a failure story

An order identifier partitions lookup naturally, but partitioning writes requires more thought. A database unique constraint on the idempotency key can arbitrate concurrent equivalent attempts across replicas. Checking for a key in application code and inserting later leaves a race: both processes can observe absence. The transaction must create or retrieve the authoritative result atomically according to the API's contract. Reusing a key with a different payload should produce a defined conflict, not silently accept the second meaning.

Notification workers need exclusive temporary ownership of a job, retry eligibility and durable completion evidence. A queue receipt or database lease provides ownership for a bounded interval; it does not prove the worker is still alive indefinitely. If a lease expires while a slow provider call is running, another worker can begin the same notification. Consumer idempotency and a provider-supported idempotency mechanism, where available, limit duplicate effects. An in-memory mutex coordinates threads in one process and offers no protection between machines.

Partitioning by tenant can keep related work together and reduce cross-partition coordination. It can also strand capacity when one tenant is much larger than others. Hashing many keys across partitions improves distribution but complicates movement and ordered processing. Choose an ordering scope explicitly: per order, per customer, or globally. Global serialization often defeats horizontal throughput. A customer's events may need ordered application while unrelated customers proceed independently.

Balance work rather than counting requests alone. Ten cached reads can be cheaper than one report over a large historical range. Persistent connections may remain attached to one target while newly added targets appear idle. A worker processing one long job can be saturated with a queue depth of one. Compare per-replica in-flight work, CPU demand, latency and completion rates, with bounded instance identifiers in infrastructure telemetry. Customer IDs belong in controlled diagnostic records rather than unrestricted metric dimensions.

## Startup, readiness and draining are separate transitions

A new process is useful after configuration loads, required resources become available, and it can accept routed work. Listening on a TCP port is weaker evidence. `/healthz` reports that the process is alive; `/readyz` reports whether it should receive new traffic. During shutdown, readiness should become false before the process exits. Routing convergence, connection draining and the application's own grace period must fit together.

AWS's [ECS connection-draining guidance](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/load-balancer-connection-draining.html) describes load-balancer deregistration and application stop responsiveness. The [Kubernetes pod lifecycle documentation](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) explains pod termination and endpoint behavior. Their mechanisms differ, so do not copy a timeout from one platform into another without evaluating request duration and the installed platform's behavior. Long uploads and streams require a different policy from short order requests.

The following complete Go program demonstrates the application side on loopback. Save it as `lifecycle.go`. It needs an installed supported Go toolchain; it has no third-party dependencies. Use the same `go run` command on all three Linux families. It handles GET requests only and does not implement orders or database readiness. The readiness flag models the routing transition, while the shutdown deadline bounds completion of existing HTTP handlers.

```go
package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os/signal"
	"sync/atomic"
	"syscall"
	"time"
)

func main() {
	var ready atomic.Bool
	ready.Store(true)
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			w.Header().Set("Allow", http.MethodGet)
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		fmt.Fprintln(w, "alive")
	})
	mux.HandleFunc("/readyz", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			w.Header().Set("Allow", http.MethodGet)
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		if !ready.Load() {
			http.Error(w, "draining", http.StatusServiceUnavailable)
			return
		}
		fmt.Fprintln(w, "ready")
	})
	server := &http.Server{
		Addr: "127.0.0.1:8080", Handler: mux,
		ReadHeaderTimeout: 2 * time.Second,
	}
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGTERM,
		syscall.SIGINT)
	defer stop()
	drained := make(chan struct{})
	go func() {
		defer close(drained)
		<-ctx.Done()
		ready.Store(false)
		// Lab delay stands in for measured routing convergence.
		time.Sleep(2 * time.Second)
		drain, cancel := context.WithTimeout(context.Background(),
			5*time.Second)
		defer cancel()
		if err := server.Shutdown(drain); err != nil {
			log.Printf("graceful shutdown incomplete: %v", err)
			_ = server.Close()
		}
	}()
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatal(err)
	}
	<-drained
}
```

```bash
go run lifecycle.go
```

Use a second terminal to request `curl --fail --show-error http://127.0.0.1:8080/readyz`. Press Ctrl-C in the foreground server terminal to trigger the lab shutdown. During the two-second demonstration delay, readiness responds unavailable; afterwards the listener closes. A `curl --fail` request then returns a nonzero status. These are expected behaviors to verify, not recorded test results. The main goroutine waits for the drain routine: returning from the listener alone would end the process before shutdown finished. The delay is deliberately illustrative; production should derive it from routing behavior and retain durable work when the grace deadline expires. Do not equate cancellation of an HTTP request with cancellation of a committed order.

## Add replicas in a bounded experiment

Start from a measured baseline and change one dimension. Add one replica, wait until it is genuinely ready, and hold the same arrival profile long enough to see queue and database effects. Confirm traffic reaches it. Compare successful attempts per second, latency distribution, rejection fraction, connection use and notification age. An improved API response coupled with growing notification delay may merely move the bottleneck downstream.

Then remove one replica under controlled staging traffic. Observe readiness withdrawal, active-request behavior, job lease expiration and replacement routing. Reconcile accepted orders and notification results. This failure experiment is essential: a normal balanced test will not expose local state lost on removal. For production, use the team's existing deployment and failure-testing approvals; the chapter's local lifecycle program is a mechanics lab.

A typical scaling failure shows all new replicas healthy, database connection failures rising, and throughput unchanged. Diagnosis should connect the pool maxima and rollout surge to the connection ceiling rather than declare the load balancer broken. Recovery may cap routing or replica count, reduce unnecessary idle connections and roll back the deployment surge. Restarting every replica simultaneously creates connection storms and discards useful diagnostic evidence.

Another failure shows one tenant's queue age rising while total CPU remains low. Inspect partition assignment and long-running work before adding general-purpose replicas. Rebalance with an explicit ownership handoff so two workers do not believe they own the same partition. Preserve ordering where the contract requires it and document where it does not.

## Exercises and answer guidance

Eight API replicas each permit twenty connections, with four ten-connection worker pools and a database budget of180. Explain why “CPU is only thirty percent” does not make this plan safe. The possible connection demand is200 before rollout; CPU measures another resource. Reduce or restructure pools and evaluate actual wait behavior.

A process passes liveness immediately but requires thirty seconds to load routing data. Which probe should gate traffic? Readiness should remain false until it can accept the intended work. Repeated liveness failures during legitimate startup can create a restart loop; use platform startup semantics where appropriate.

A worker lease expires after thirty seconds, but a provider call can last forty. Name the duplicate-effect scenario and two controls. Another worker can acquire the job before the first finishes. Bounded provider deadlines, lease renewal with correct ownership checks, and idempotent external effects are candidate controls; merely raising worker count worsens exposure.

## Takeaways and verification

Useful replicas require replaceable process state, deliberate work ownership, balanced demand and a budget for shared resources. Count temporary rollout capacity and test removal as carefully as addition. Primary ECS, Kubernetes, [Go HTTP shutdown](https://pkg.go.dev/net/http#Server.Shutdown) and [signal context](https://pkg.go.dev/os/signal#NotifyContext) documentation were inspected on2026-10-01. The Python arithmetic and Go lifecycle examples are inline; no live replica rollout, database coordination test or load-balancer integration was executed during authoring.
