---
book: The Complete DevOps Engineering Book
volume: 8
volume_title: "Infrastructure as Code"
chapter: 80
title: "Infrastructure Lifecycle and Disaster Recovery"
slug: infrastructure-lifecycle-and-disaster-recovery
status: complete
summary: ../../_ai/chapter-summaries/080-infrastructure-lifecycle-and-disaster-recovery.md
---

# Chapter 80 — Infrastructure Lifecycle and Disaster Recovery

## Bootstrap dependencies and break-glass access

Summit's infrastructure pipeline cannot run because its state bucket is inaccessible. The bucket's policy is managed by the same pipeline. The team has created a recovery dependency cycle: the tool needed to repair access first needs the access it is trying to repair. Infrastructure recovery begins with identifying such cycles, not with assuming that a repository can recreate everything.

A bootstrap root establishes the minimum external dependencies required by ordinary roots: state storage, execution identity, encryption access, and perhaps artifact retrieval. Give it separate lifecycle ownership and a recovery path. Do not let application teardown remove the backend, audit log destination, or the only role capable of restoring the environment. A smaller bootstrap scope is easier to inspect during an incident, but it still needs backups and authorized administrators.

Break-glass access is a controlled alternate path when normal automation cannot function. It must remain usable under the failure being planned for, have a documented custodian, and produce audit evidence. An emergency identity stored only in the failed cluster or accessible only through a failed identity service is not an alternate path. Rehearse access and expiry; an untested password in a document can fail precisely when the team depends on it.

Harbor's recovery can require a clean VPS, an offline copy of configuration, an available application artifact, and a database backup. Summit also needs AWS account access, region/service availability, state, and managed-service restore permissions. Atlas needs a way to reconstruct cluster infrastructure and restore workload configuration without relying on the old cluster's controllers. These paths share a product but have different dependency graphs. [Disaster recovery and failback](../19-site-reliability-and-recovery/187-disaster-recovery-and-failback.md) owns the broader recovery objectives and coordination model.

Build a recovery dependency table for the actual environment. For each item, record its authoritative copy, required identity, location, latest verified restoration, and what fails if it is absent. Source code, state, application artifacts, database backups, DNS authority, secrets, certificates, and external notification credentials are separate entries. “Everything is in Git” is rarely true once durable data and privileged identity enter the system.

## State recovery and teardown

State recovery repairs the infrastructure engine's record. It does not automatically repair infrastructure or application data. Before modifying state, stop competing jobs, preserve the current snapshot even if damaged, identify the last trusted copy, and compare its inventory with remote objects and audit records. A snapshot with the newest timestamp is not necessarily the newest valid state; a failed write or wrong-root upload can be newer than a useful copy.

Use an ordinary operator workstation with a compatible Terraform executable in the correct initialized root. Create a restricted evidence directory outside source-controlled paths and export the current state:

```bash
umask 077
mkdir -p ./recovery-evidence
terraform version > ./recovery-evidence/tool-version.txt
terraform state pull > ./recovery-evidence/current.tfstate
terraform state list > ./recovery-evidence/current-addresses.txt
```

`umask` restricts new file permissions; the named directory collects sensitive incident evidence. `version` records the executor baseline, `state pull` exports the configured backend's current state, and `state list` records addresses for comparison. Inspect command success before relying on the files. If the backend is inaccessible, the failed command itself establishes the access problem; it does not produce a valid backup. [State and locking](073-state-locking-and-remote-backends.md) covers normal export and locking assumptions.

A versioned backend can supply an earlier object version. Preserve the original version identifier and its audit context, and retrieve a candidate into a restricted file rather than immediately overwriting the live backend. S3's [previous-version restoration documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RestoringPreviousVersions.html) explains object-version recovery. Which version is appropriate remains an incident decision based on inventory and completed operations.

The following complete Python inspection helper reads two state exports and compares lineage, serial, and top-level tracked addresses without printing attribute values. Save as `compare_state.py` in the evidence directory:

```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("Usage: python3 compare_state.py CURRENT CANDIDATE")

def load(path):
    try:
        state = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot inspect {path}: {exc}")
    if not isinstance(state, dict):
        raise SystemExit("State must be a JSON object")
    resources = state.get("resources", [])
    if not isinstance(resources, list):
        raise SystemExit("Malformed resources list")
    addresses = set()
    for resource in resources:
        if not isinstance(resource, dict):
            raise SystemExit("Malformed resource record")
        prefix = resource.get("module", "")
        base = f"{resource.get('type', '?')}.{resource.get('name', '?')}"
        if resource.get("mode") == "data":
            base = "data." + base
        addresses.add(f"{prefix}.{base}" if prefix else base)
    return state, addresses

current, current_addresses = load(sys.argv[1])
candidate, candidate_addresses = load(sys.argv[2])
for label, state in [("current", current), ("candidate", candidate)]:
    print(f"{label}: lineage={state.get('lineage')} serial={state.get('serial')}")
print("Only current:", sorted(current_addresses - candidate_addresses))
print("Only candidate:", sorted(candidate_addresses - current_addresses))
print("Inspection only: this does not validate state or authorize replacement.")
```

Run `python3 compare_state.py current.tfstate candidate.tfstate` from that directory after obtaining a real candidate. The helper is deliberately limited: it summarizes resource records, not every indexed instance, deposed object, output, or provider-specific structure. It does not establish that two snapshots represent the same remote inventory. It is a comparison aid, not an automated restore algorithm. Avoid claiming that an internal JSON representation is a stable application API across every tool version.

For an approved manual restoration, `terraform state push ./recovery-evidence/candidate.tfstate` uploads the candidate to the currently configured backend. This is a sensitive mutation and must be executed only after the correct root/backend, stopped writers, backup, and incident authorization are established. Terraform checks lineage and serial to reject suspicious replacement. Do not add `-force` as a routine workaround for those checks; a rejection is evidence requiring investigation. [State push reference](https://developer.hashicorp.com/terraform/cli/commands/state/push) defines the safeguards.

After a restore, plan without applying and compare it with remote inventory. A resource created after the candidate snapshot may now appear missing from state while it remains in AWS. Adopt or otherwise reconcile its identity deliberately, using [import/refactoring](075-import-drift-and-safe-refactoring.md). An immediate apply can make the restored state problem worse by creating duplicates or deleting a misunderstood object.

## Rebuilding a lost environment

A rebuild needs an ordered procedure with acceptance evidence. Start by recovering access and the bootstrap layer. Restore source at a known revision, approved CLI/provider dependencies, state, and artifact identity. Reconstruct network and identity dependencies before consumers. Restore database data before routing writes to a new application. Reconcile pending notifications so retry does not silently cause duplicate external effects. [Message compatibility](../14-delivery-deployment-and-gitops/136-database-and-message-compatibility.md) and [idempotency](../17-distributed-systems-and-data-operations/162-retries-idempotency-and-backoff.md) own those detailed contracts.

Do not switch public DNS merely because the new machines are running. Verify application configuration, access controls, data completeness, order acceptance, notification processing, telemetry, and operational access. Use synthetic requests with identifiable test data and a controlled notification destination. Confirm whether the recovered database's timeline meets the required data-loss objective. A successful infrastructure apply can still create an empty, inaccessible, or stale environment.

A recovery rehearsal should simulate the dependency loss, not merely run `plan` against healthy production. In a disposable scope, remove the ordinary runner's access or recreate a new environment from approved artifacts. Record actual elapsed time for access, provisioning, data restoration, verification, and traffic change. Document pauses caused by approvals, quota, unavailable artifacts, or forgotten credentials. Those observations improve the recovery design more than an optimistic total duration in a runbook.

For Summit, a regional rebuild can require changes to identifiers, quotas, secret replicas, certificates, and data-copy arrangements. Do not assume that changing one region variable makes every dependency portable. For Harbor, a new VPS can change IP address and storage layout. For Atlas, storage snapshots and cluster APIs may have provider-specific restoration constraints. Review each recovery target as a concrete architecture, with current cost and capacity estimates.

Ubuntu 24.04, Fedora 44, and RHEL 9 reconstruction must use the same approved baseline or a deliberately tested migration. A recovered source repository does not freeze package repositories. Record image identity, required streams, entitlement, and security policy. An unplanned distribution upgrade during recovery adds new variables at the worst time. If an old image is no longer usable, separate the compatibility problem from data recovery and test it before traffic restoration.

## Failure diagnosis and lifecycle retirement

Suppose a candidate state has a lower serial than the backend. The push is rejected. Investigate whether the backend includes later valid changes, whether the candidate belongs to the correct root, and whether the intended operation really requires rewinding knowledge. Preserve both snapshots. Do not interpret a lower serial as a corrupt file; it can simply be an older record. An incident owner must decide how to reconcile later objects.

Suppose rebuilding fails because the application image tag was deleted from the registry. Source can build a replacement, but that build may use different dependencies than the lost release. The prevention is durable artifact retention and immutable identity, not a promise that Git alone is enough. [Artifact promotion](../14-delivery-deployment-and-gitops/131-release-engineering-and-artifact-promotion.md) defines that release contract.

Retirement is also a recovery-aware procedure. Inventory consumers, export required data, revoke credentials, stop traffic, review destruction, and verify remaining resources. Use a saved destruction plan rather than an unattended `destroy` as an ordinary cleanup shortcut. For an authorized disposable root, run `terraform plan -destroy -input=false -out=retire.tfplan`, inspect `terraform show retire.tfplan`, then apply the reviewed artifact. This deletes managed resources and can permanently remove data; it is never an implied production recovery action. [Destroy reference](https://developer.hashicorp.com/terraform/cli/commands/destroy) describes the CLI behavior.

After teardown, inspect provider inventory for retained volumes, snapshots, log storage, network interfaces, and backend records. Some are intentionally retained; others keep accruing charges. Assign owners and retention dates. Keep the state backend until its managed objects and audit/recovery obligations are resolved. Deleting the evidence first makes leftover-resource diagnosis harder.

## Exercises and answer guidance

1. The backend's encryption key can be administered only through the failed pipeline. What design change is needed? Establish separately governed bootstrap/break-glass access and rehearse it under pipeline failure.
2. A recovered state predates a newly created database. What is unsafe about immediate apply? The tool may misunderstand ownership; inventory and reconcile the database before executing any proposed create/delete.
3. A rehearsal restores hosts in ten minutes but data in two hours. Which duration governs service recovery? The validated service restoration path, including data and traffic acceptance, not host provisioning alone.

Review questions: Which assets cannot be reconstructed from source? Why preserve a damaged snapshot? What do lineage/serial safeguards detect? Why must retirement include inventory after deletion?

Infrastructure lifecycle is reliable when bootstrap dependencies remain accessible, identity records and data have separate recovery paths, and both restoration and retirement end with observable service or inventory evidence.

## Sources and verification

Terraform state push/destroy, S3 previous-version restoration, and [AWS recovery-strategy guidance](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_planning_for_recovery_disaster_recovery.html) were inspected 2026-10-01. Python helper and CLI examples are inspection/rehearsal material, not claims of a performed restore. No state mutation, teardown, cloud rebuild, or data restoration ran during authoring.
