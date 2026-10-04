---
book: The Complete DevOps Engineering Book
volume: 12
volume_title: "Kubernetes Production Engineering"
chapter: 114
title: "CSI and Production Storage"
slug: csi-and-production-storage
status: complete
summary: ../../_ai/chapter-summaries/114-csi-and-production-storage.md
---

# Chapter 114 — CSI and Production Storage

## Persistent storage is a service boundary

A Pod's writable container layer is replaceable. If a workload needs data to survive Pod recreation, node maintenance or cluster failure, it needs a storage design whose durability and recovery behavior are explicit. Kubernetes provides APIs to request and attach storage; it does not make every backend durable, replicated, encrypted, portable or recoverable. The storage team, platform team and application owner must agree on performance, topology, data protection and failure handling before a PersistentVolumeClaim is treated as production-ready.

The Container Storage Interface (CSI) lets storage vendors integrate drivers with Kubernetes. A driver may provision volumes, attach and detach them, mount them on nodes, expand them, expose topology and support snapshots or cloning. These are separate capabilities. Verify the exact driver version, Kubernetes compatibility, supported node operating systems, volume modes, access modes, topology behavior and optional operations from the driver's release documentation. An API object existing in the cluster does not prove the driver implements a requested operation or that the backend meets an application's latency and durability requirements. Kubernetes' [storage concepts](https://kubernetes.io/docs/concepts/storage/) and the CSI [driver documentation](https://kubernetes-csi.github.io/docs/drivers.html) provide the API context; the selected driver documentation defines its support.

Application teams normally request a `PersistentVolumeClaim` (PVC). A `StorageClass` names a provisioner and policy such as reclaim behavior, topology binding and expansion. The provisioner creates or selects a `PersistentVolume` (PV), which represents the backing volume. A static PV can be created by an administrator; a dynamic PV can be provisioned from a PVC. A claim is an allocation request, not a backup. A bound claim establishes control-plane binding, not successful mount, application write, backend replication or restore.

Access modes describe how a volume may be mounted or used under the driver's and Kubernetes' rules. They are not an authorization system and should not be treated as a lock around application writes. A storage backend may offer a shared filesystem, a block volume attachable to one node, or another model; the actual supported semantics depend on driver and backend. `ReadWriteOnce` does not mean only one Pod in every circumstance; it describes read-write mounting by a single node, and multiple Pods on that node may use it. `ReadWriteMany` requires a driver and backend that support multi-node read-write access. `ReadWriteOncePod` provides a single-Pod mount constraint when supported. Confirm current semantics and driver support in the [PersistentVolume documentation](https://kubernetes.io/docs/concepts/storage/persistent-volumes/), and enforce application-level consistency separately.

## Topology, performance and lifecycle

Many block volumes are attached within a region or zone and cannot be mounted from every node. Storage topology must therefore agree with Pod scheduling. With immediate binding, a claim may be provisioned before the scheduler knows where the Pod can run. A topology-constrained volume can then conflict with node affinity, capacity or zone constraints. Where supported, `WaitForFirstConsumer` delays binding or provisioning until a consuming Pod's scheduling constraints are available. It does not override a driver's limits or create capacity; validate the selected driver behavior and scheduler constraints. Avoid setting `nodeName` for a Pod using delayed binding because this bypasses normal scheduling decisions and can leave the claim pending. See the Kubernetes [StorageClass guide](https://kubernetes.io/docs/concepts/storage/storage-classes/).

Storage classes should express supported service tiers in understandable terms: performance range, durability model, encryption, topology, expansion and reclaim behavior. Avoid labeling a class "fast" or "gold" without measurable service characteristics and an owner. Provider parameters are driver-specific and are not validated generically by Kubernetes. An invalid mount option or unsupported parameter may surface only during provisioning or mount. Keep a tested default class policy, and make critical applications request the intended class explicitly so a default change does not silently alter cost, performance or recovery.

`Delete` and `Retain` reclaim policies have real data consequences. With `Delete`, releasing a dynamically provisioned PV can cause the backend volume to be deleted when the provisioner supports that action. With `Retain`, the PV and underlying storage require administrative reclamation and cleanup. Choose based on data classification, application lifecycle and deletion safeguards; a policy is not a backup. Test PVC deletion and re-creation procedures outside production, including how data is reattached and who approves destructive cleanup. The exact lifecycle can depend on finalizers, driver behavior and backend API success.

Storage performance is an end-to-end property. A volume's advertised IOPS or throughput cannot guarantee application latency if the node, network, queue depth, filesystem, workload pattern or backend is limiting. Measure representative read/write size, concurrency, fsync behavior, tail latency and saturation under realistic load. Include attach/mount time in recovery objectives. Check node volume limits, zone placement, encryption overhead, filesystem capacity and inode exhaustion. Alert on PVC capacity, backend health, volume attach failures, latency and driver reconciliation errors. Establish what happens when a claim is full: databases may stop writes, logs can exhaust node storage, and filesystem behavior under pressure can differ from block-device behavior.

Expansion is not a general resize or shrink facility. A class must allow expansion, and the CSI driver and filesystem path must support it. Kubernetes can request a larger capacity through the PVC, but backend expansion, node-side filesystem resize and workload-visible capacity may progress asynchronously. Observe the PVC and PV conditions and driver events; do not delete and recreate a production claim to force a size change. Plan capacity with headroom and test the expansion flow before an incident. Where a CSI driver supports volume attributes changes, Kubernetes' `VolumeAttributesClass` is a separate feature with its own cluster and driver support requirements.

## Snapshots, consistency and recovery

CSI volume snapshots use the `VolumeSnapshot`, `VolumeSnapshotContent` and `VolumeSnapshotClass` APIs. The snapshot API and controller components may need to be installed by the Kubernetes distribution or storage integration; they are not simply built into every cluster. Snapshot support is CSI-driver-specific and backend-dependent. A `VolumeSnapshotClass` selects a driver and deletion policy. With `Delete`, deleting the snapshot API object can delete its backing snapshot; `Retain` preserves the backend object for manual lifecycle management. Check which class will be used and its deletion behavior before creating snapshots at scale. Read the Kubernetes [snapshot documentation](https://kubernetes.io/docs/concepts/storage/volume-snapshots/) and selected driver guide.

A storage snapshot is usually a point-in-time copy of a volume, but that does not automatically make a running application backup consistent. A database may have buffered writes, multiple related volumes or external transaction logs. Use the database's supported backup or freeze procedure, application quiescing where needed, and a coordinated snapshot set when the recovery point spans volumes. Verify whether the backend snapshot is crash-consistent, application-consistent or has a stronger documented guarantee. Protect snapshot credentials and permissions, keep copies in a failure domain separate from the source when required, and define retention against data-loss and legal requirements.

A successful snapshot condition is evidence that the controller reported completion, not evidence that data can be restored. Recovery requires a usable snapshot, compatible storage driver and region/topology, keys and credentials, a claim or restore process, application startup and data validation. Practice restoring into an isolated namespace or recovery cluster without overwriting production data. Measure the time from incident declaration through readable application data, and verify checksums or application-level invariants. [Chapter 120](120-upgrades-etcd-and-cluster-recovery.md) covers cluster recovery; [Chapter 186](../19-site-reliability-and-recovery/186-backup-engineering.md) covers workload backup engineering. Kubernetes API-state backup, volume snapshots and database-native backup solve different problems and may all be required.

For DispatchDesk, the order service writes transactions to a database on a CSI-backed block volume. The team learns that a volume snapshot completes quickly, but a restore exercise cannot recover the latest committed transactions because the database's write-ahead log lived on a separate unprotected volume. The incident response pauses unsafe writes if possible, preserves both data and logs, identifies the last verified recovery point and restores into an isolated environment using the database vendor's procedure. The corrective design coordinates snapshot or backup of the database and log state, documents key and topology dependencies, and tests application integrity after restoration. Increasing snapshot frequency alone would preserve more inconsistent state without proving recoverability.

## Read-only checks and an attachment incident

If a Pod cannot start because a claim is pending or a volume will not mount, inspect the Kubernetes objects before changing a class or deleting a claim. From an authorized workstation with a verified context, use read-only commands such as:

```bash
kubectl --context kind-dispatchdesk --namespace production get pvc
kubectl --context kind-dispatchdesk --namespace production describe pvc dispatchdesk-data
kubectl --context kind-dispatchdesk get pv
kubectl --context kind-dispatchdesk get storageclasses
kubectl --context kind-dispatchdesk --namespace production get pods -o wide
kubectl --context kind-dispatchdesk get events --all-namespaces --sort-by=.lastTimestamp
```

The context name is illustrative; verify the API endpoint and account before use. PVC and PV status, events, StorageClass settings and Pod placement can narrow the issue to provisioning, topology, binding, attach or mount. Events may expire, details differ by driver and distribution, and object status cannot establish backend data integrity or application consistency. Review output before sharing because volume names, node locations and annotations may be sensitive.

Suppose the DispatchDesk database Pod is pending with an unbound claim after a scheduler change. Compare the claim's requested class and access mode with the PV or provisioner, inspect StorageClass binding mode and topology, and review Pod scheduling constraints and events. If a PV is bound but the Pod reports attach or mount errors, check node placement, zone compatibility, attachment limits, driver controller/node health, credentials, backend quota and provider events. Do not immediately delete the PVC, PV or VolumeAttachment: these objects may represent the only reference to production data, and deletion can trigger detach or backend deletion. Involve the storage owner and preserve the claim/backend mapping while collecting evidence.

Recovery should match the failure layer. Correct a scheduling/topology mismatch through a reviewed workload constraint or supported storage design. Restore the driver or backend integration when attach/mount fails, using the storage provider's recovery procedure. If data is unavailable or corrupted, follow the tested backup restore path and validate the application before returning traffic. After recovery, record the actual recovery point, duration and cause; update alerts, ownership and exercises. Never use a successful mount as the only test of a database restore or a snapshot as the only evidence of backup readiness.

## Exercises and answer guidance

1. A claim is bound but the Pod cannot mount it. What is established, and what is not? Control-plane binding succeeded; provisioning, topology, attach, node plugin, filesystem mount and application access may still fail.
2. A team assumes `ReadWriteOnce` means one Pod can ever mount the claim. Is that safe? No. It is a node-level access mode; multiple Pods on one node may use it. Confirm exact driver semantics and use application coordination.
3. A claim is pending after its Pod gained a zone affinity. What StorageClass behavior may help? For a compatible driver, `WaitForFirstConsumer` can align provisioning/binding with scheduling topology; it cannot create missing capacity or fix unsupported constraints.
4. A volume snapshot is marked ready. Has database recovery been demonstrated? No. Restore in isolation, recover all related state and keys, start the database, validate transactions and measure recovery objectives.
5. A PVC is deleted and the PV has a `Delete` reclaim policy. What must the team consider? Whether the provisioner will delete the backing volume and snapshot/data, plus finalizer and backend lifecycle behavior; inspect policy and approvals before deletion.

Review questions: what does CSI provide, how do StorageClass and topology affect scheduling, what do access and reclaim modes mean, and what evidence proves application data recovery?

## Verification and primary sources

Official Kubernetes storage, StorageClass and snapshot documentation and CSI driver references were inspected on 2026-10-04. The commands are read-only examples and were not run against a cluster. No claim, volume, driver, snapshot, backend, application or storage policy was changed. Static checks cannot establish a selected CSI driver's feature support, capacity, performance, encryption, durability, application consistency or restore capability.

Primary references: [Kubernetes storage](https://kubernetes.io/docs/concepts/storage/), [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/), [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/), [Volume Snapshots](https://kubernetes.io/docs/concepts/storage/volume-snapshots/), [Volume Snapshot Classes](https://kubernetes.io/docs/concepts/storage/volume-snapshot-classes/), [CSI drivers](https://kubernetes-csi.github.io/docs/drivers.html), and [CSI driver capabilities](https://kubernetes-csi.github.io/docs/developing.html).
