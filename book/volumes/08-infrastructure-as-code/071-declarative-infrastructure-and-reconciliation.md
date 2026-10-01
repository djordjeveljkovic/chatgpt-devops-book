---
book: The Complete DevOps Engineering Book
volume: 8
volume_title: "Infrastructure as Code"
chapter: 71
title: "Declarative Infrastructure and Reconciliation"
slug: declarative-infrastructure-and-reconciliation
status: complete
summary: ../../_ai/chapter-summaries/071-declarative-infrastructure-and-reconciliation.md
---

# Chapter 71 — Declarative Infrastructure and Reconciliation

## Desired state and dependency graphs

DispatchDesk's first VPS can be created by a person, configured with a shell script, and recorded in a spreadsheet. This is a reasonable starting point when there is one host and a deliberate maintenance window. The weakness appears during recovery: the spreadsheet describes what somebody remembers, the script describes what somebody once did, and the running host contains what actually happened. Infrastructure as code makes the intended environment reviewable and gives a tool enough information to compare that intention with observations.

A declarative specification describes a target: one application network, two application instances, a database endpoint, and a DNS record. It does not necessarily contain the exact sequence of API calls that will reach that target. The engine and its providers derive operations from configuration, recorded identity, and remote observations. That distinction explains both the benefit and the danger. A readable declaration can still cause deletion or replacement when the tool determines that an object no longer belongs in the desired environment.

Consider a request to increase DispatchDesk's web capacity. The business requirement is that the order endpoint remains available while an additional process starts. “Two instances” describes capacity, but says nothing about readiness, traffic draining, database connection limits, or whether both instances fit in one failure domain. Infrastructure code is an implementation of the requirement; it does not replace the requirement. Link the change to an acceptance test, such as sending authenticated synthetic orders through the public endpoint while observing successful processing and notification delivery.

Dependencies form a graph. A subnet requires a network; an instance requires a subnet; a DNS record may require a load balancer's generated hostname. A reference to a resource attribute is usually a better way to express such a relationship than copying an identifier into a variable. It communicates why the consumer must follow the producer. Unrelated nodes can run concurrently, while graph edges constrain order. A broad explicit dependency can reduce useful concurrency and conceal the precise relationship. Use one when the dependency is real but cannot be inferred from an attribute reference.

Here is an intentionally tool-neutral model for the managed AWS company. This is pseudocode, not a file accepted by a CLI:

```text
network = Network(cidr = "10.42.0.0/16")
application_subnet = Subnet(network_id = network.id, cidr = "10.42.10.0/24")
application_pool = ComputePool(subnet_id = application_subnet.id, replicas = 2)
endpoint = LoadBalancer(targets = application_pool.instance_ids)
dns = Record(name = "orders.example.invalid", target = endpoint.hostname)
```

The graph describes construction order, but it does not mean that receiving a load balancer hostname proves that the application can serve an order. API-level success, resource-level readiness, and application-level correctness are separate observations. A provider may wait for a resource to reach an API status and still leave the engineer responsible for checking the application's contract. The owning chapters for concrete [AWS load balancing](../09-aws-foundations/089-route-53-certificates-and-load-balancers.md) and [container contracts](../05-container-internals-and-oci/050-the-container-contract.md) supply those checks.

Deletion traverses dependencies in an appropriate reverse order, subject to provider behavior and external constraints. A retained database, another team's manually attached interface, or a deletion-protection setting can prevent complete teardown. A failed teardown is an operational event, not proof that the declaration was ignored. Capture the remaining resource identifiers and determine whether they are intentionally retained before retrying.

Terraform documents that a resource may be created, updated, removed, or replaced depending on configuration and remote API capabilities. Its plan previews proposed operations; review replacement as a distinct risk from an in-place update. [Terraform resource overview](https://developer.hashicorp.com/terraform/language/resources) and [plan reference](https://developer.hashicorp.com/terraform/cli/commands/plan) describe the exact tool behavior. This chapter's model applies more broadly, but individual engines differ in their treatment of observation, state, and continuous reconciliation.

## Idempotency and ownership

An idempotent operation can be repeated without adding an unintended new effect after the intended state has been reached. “Ensure this directory exists” is easier to repeat safely than “append this configuration line.” However, idempotency is a property of the operation and its assumptions, not a magic property of a file extension. A declarative resource that invokes a command with side effects can still send duplicate notifications or recreate data. A shell script can be carefully idempotent.

Infrastructure ownership means that one authority decides the desired value of a field or object. DispatchDesk's platform team might own a service's minimum capacity while an autoscaler owns its current capacity. If a nightly infrastructure job keeps restoring the current capacity to two while an autoscaler raises it to six, the system has two writers with incompatible intentions. The resulting oscillation is not solved by retrying faster. Agree which controller owns the field, use the tool's documented mechanism to accommodate that arrangement, and verify that a planned change no longer fights the autoscaler.

Ownership also determines whether deletion is permitted. A resource imported into a team's state is not automatically safe to destroy: it may host another service, contain irreplaceable data, or be a shared network dependency. Before adoption, inventory consumers and obtain the organizational authority to manage its lifecycle. [Import and safe refactoring](075-import-drift-and-safe-refactoring.md) covers identity changes; [state and locking](073-state-locking-and-remote-backends.md) covers how the tool records those identities.

Continuous reconcilers and run-to-completion tools have different operating rhythms. A Kubernetes controller repeatedly observes an API object and works toward its desired state. A typical local infrastructure CLI performs a bounded run when invoked. A plan that was clean yesterday does not continuously guarantee that nobody changed a firewall this morning. Drift detection therefore needs a schedule, an owner, and an interpretation policy. Some drift is an urgent unauthorized change; some is an intentional emergency mitigation awaiting incorporation into code.

For DispatchDesk's VPS company, a small reviewed provisioning workflow plus host configuration management may be enough. The managed AWS company benefits from tracking API resources and their identities. The Kubernetes company uses reconciliation for workloads and infrastructure tooling for the cluster's surrounding networks and identities. None of these arrangements requires every layer to use one engine. A useful boundary is the one that makes ownership and recovery comprehensible to the team that will be paged.

## Comparing scripts with declarative tools

The following small lab demonstrates the problem without creating cloud resources. Run it as an ordinary user on either Ubuntu or Fedora/RHEL, in a disposable directory. It requires a POSIX shell and standard file tools, not administrator access. It creates only a local text file representing a setting. It does not configure a real service.

```bash
mkdir -p "$HOME/dispatchdesk-reconciliation-lab"
cd "$HOME/dispatchdesk-reconciliation-lab"
printf '%s\n' 'workers=2' >> service.conf
printf '%s\n' 'workers=2' >> service.conf
cat service.conf
```

`mkdir -p` creates missing directories and accepts an existing directory. The quoted path preserves spaces in the home path. `cd` chooses the execution directory, so subsequent relative filenames refer to this lab. `printf` prints one newline-terminated setting; `>>` appends without checking whether that setting already exists. `cat` displays the result. Expect two lines with the same setting, because executing the procedure twice duplicated the operation. These commands are the same on the stated Linux families; package managers and security policy are irrelevant to this user-owned file exercise.

A more deliberate implementation writes the entire owned file and changes it only when necessary. Save this complete script as `reconcile.sh` in that directory:

```sh
#!/bin/sh
set -eu
wanted='workers=2'
target='./service.conf'
temporary=$(mktemp './service.conf.XXXXXX')
trap 'rm -f "$temporary"' EXIT HUP INT TERM
printf '%s\n' "$wanted" > "$temporary"
if [ -f "$target" ] && cmp -s "$temporary" "$target"; then
    printf '%s\n' 'Configuration already matches.'
else
    mv "$temporary" "$target"
    printf '%s\n' 'Configuration reconciled.'
fi
```

`set -e` requests termination on many command failures, with shell-specific exceptions; `set -u` catches expansion of unset variables. Neither replaces explicit error handling in a production automation program. `mktemp` creates a unique file in the same directory as the target. The trap removes that temporary file on exit or interruption. `cmp -s` silently compares bytes: success means no replacement is needed. `mv` replaces the target after the complete desired content has been written. Keeping the temporary file on the same filesystem avoids relying on a cross-filesystem move for publication. This toy implementation does not preserve an existing file's ownership or mode, take a concurrency lock, validate application syntax, or restart a service.

Run and inspect it:

```bash
sh ./reconcile.sh
sh ./reconcile.sh
cat ./service.conf
printf '%s\n' 'workers=9' > ./service.conf
sh ./reconcile.sh
cat ./service.conf
```

The first run should replace the duplicate-line file; the second should report that it matches. The manual edit introduces drift. The next run should restore the declared value. These are expected observations, not captured test output. Inspect the file after each operation instead of treating a printed success line as sufficient evidence. Cleanup deletes only the two lab files:

```bash
rm -f ./service.conf ./reconcile.sh
```

The destructive scope is the named files in the current directory. Verify the working directory before running cleanup; do not generalize this into a recursive deletion command.

Now introduce a failed assumption: another script expects to append `log_level=debug` to this file. Our reconciler replaces the entire file, so it removes that setting. Both programs work according to their individual instructions, but the combined system loses configuration. The diagnosis is an ownership conflict. Recovery is to decide whether one program owns the complete file, whether separate include files are supported, or whether one structured configuration renderer must combine both values. Repeating the reconciler cannot repair an unclear ownership contract.

A production configuration manager adds resource-specific inspection, privilege handling, service handlers, and reporting around this pattern. An infrastructure engine adds provider APIs, identity tracking, and dependency planning. A script remains valuable for a narrow procedural task, such as extracting a diagnostic archive, where each step has a clear execution order and the result is not a long-lived managed object. Compare tools by the kind of state they manage and the evidence they expose, rather than by how little code a demonstration contains.

## Failure, recovery, and change review

Suppose an apply creates the network but fails while creating the second instance because an account limit has been reached. Do not assume that the run was transactional. Preserve logs, inspect the remote inventory, and inspect the tool's recorded state. Confirm whether the first instance is healthy and whether traffic can safely remain on it. Resolve the limit or reduce the desired capacity only after deciding the availability consequence. A fresh plan should describe the remaining work; review it before another apply.

The dangerous recovery is deleting the state file because the apply “failed.” That discards identity information while leaving billable resources behind. The next run may attempt duplicates or fail on name collisions. State recovery deserves its own procedure, including backups and access controls, as explained in [infrastructure lifecycle and disaster recovery](080-infrastructure-lifecycle-and-disaster-recovery.md). Application data recovery is another procedure entirely: reconstructing an empty database resource does not restore orders.

A reviewer should ask what changes, which objects are replaced, what survives a partial failure, who owns manual emergency changes, and how success will be measured. A plan can identify an infrastructure action without predicting a customer-visible outcome. Include application checks and rollback constraints in the change record. For a database replacement, the relevant question is not merely whether the plan is syntactically valid; it is whether a restore has been rehearsed and the recovery time fits the service requirement.

## Exercises and answer guidance

1. Change the lab's desired value to four workers, run it twice, and explain both observations. The first run should publish the new file; the second should leave it unchanged. Confirm the bytes, not only the messages.
2. Two controllers own the desired replica count. One responds to queue depth and one restores a fixed value hourly. Propose a fix. Separate the scaling controller's owned field from the platform's minimum/maximum policy; verify that infrastructure planning no longer resets the active scale decision.
3. An apply reports failure after creating a database. Should the next step be destroy? Explain. Inventory and identity inspection come first. Determine whether the database contains data or serves consumers, then choose recovery from evidence. Failure of the run does not authorize disposal of the resource.

Review questions: What information does a dependency graph communicate? Why is a successful API operation weaker evidence than a successful order? How can an idempotent script still conflict with another writer? Why must drift have an owner?

The durable lessons are to make desired state reviewable, give each resource a clear lifecycle owner, distinguish planning from application verification, and recover from partial operations using recorded identities. A declarative system reduces hidden procedure only when its boundaries and operational checks are explicit.

## Sources and verification

Official Terraform resource and plan documentation linked above was inspected on 2026-10-01. The conceptual examples do not depend on a specific provider or cloud account. The coordinator executed the inline reconciler under system `sh` in a temporary directory on 2026-10-01: duplicate-file replacement, unchanged second run, and recovery from manual `workers=9` drift all passed. This is local file-lab evidence only. No infrastructure CLI, cloud API, or cluster integration was run.
