---
book: The Complete DevOps Engineering Book
volume: 11
volume_title: "Kubernetes Foundations"
chapter: 109
title: "Persistent Volumes and Stateful Workloads"
slug: persistent-volumes-and-stateful-workloads
status: complete
summary: ../../_ai/chapter-summaries/109-persistent-volumes-and-stateful-workloads.md
---

# Chapter 109 — Persistent Volumes and Stateful Workloads

## Claims, classes and binding

Container filesystems are disposable. A replacement Pod has a new identity and may run on another node; local writable layers and `emptyDir` do not preserve application data after the Pod is removed, as described in [Chapter 103](103-pods-and-application-lifecycles.md). A PersistentVolumeClaim (PVC) lets a workload request storage without embedding provider-specific volume details in the Pod. A PersistentVolume (PV) represents storage available to the cluster, and a StorageClass describes how a provisioner can create volumes on demand. Storage connects application lifecycle to infrastructure lifecycle, so deletion, backup, topology, encryption, recovery and cost must be understood before a workload uses it.

A namespaced PVC describes capacity, access mode, volume mode and optionally a StorageClass. A controller can match it to a pre-created PV or request dynamic provisioning through the class. The claim is bound to one volume and remains the workload's reference even if a Pod is replaced. A common claim might request `20Gi` with `ReadWriteOnce` and a cluster-provided class named `standard`, but neither the capacity nor the class is portable across clusters. Check which StorageClasses exist and what their provisioners, topology, reclaim policy, encryption and backup guarantees actually mean. A default StorageClass may be selected when the PVC omits `storageClassName`; do not assume the default is free, durable or appropriate.

The following PVC is a teaching example for an isolated cluster where a StorageClass named `standard` exists and supports the requested mode and capacity. A different default StorageClass does not satisfy this explicit name. To request the cluster's default instead, omit `storageClassName` deliberately and inspect which class is marked default before creating the claim:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dispatchdesk-db-data
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 20Gi
```

Creating this claim can provision billable storage through the configured driver. Do not apply it until the class and deletion behavior are known. The PVC may remain Pending if no matching PV or provisioner exists, capacity is unavailable, the driver fails, or topology cannot be satisfied. A ResourceQuota violation normally rejects PVC creation at admission rather than leaving a created PVC Pending; inspect the API error in that case. For a persisted Pending claim, inspect `kubectl describe pvc` and its events before changing the size or class. For topology-constrained storage, a StorageClass with `volumeBindingMode: WaitForFirstConsumer` delays provisioning/binding until the scheduler evaluates a Pod that uses the claim. This can coordinate node and volume placement; setting `nodeName` directly bypasses normal scheduler binding and can leave such a claim Pending.

Access modes describe how a volume may be mounted, not a universal distributed locking guarantee. `ReadWriteOnce` generally permits read-write mounting by one node; more than one Pod on that same node may use it if the storage driver and application allow. `ReadWriteOncePod` restricts mounting to a single Pod when the CSI driver and Kubernetes support it. `ReadWriteMany` and `ReadOnlyMany` depend on the backend and driver. A mode such as `ReadWriteOnce` does not serialize writes made by processes or provide database consistency. `volumeMode: Filesystem` is the common file path case; `Block` exposes a raw block device and requires application-level management.

After binding, a Pod references the PVC by name and mounts it at a path:

```yaml
spec:
  containers:
    - name: database
      image: registry.example.invalid/dispatchdesk/database@sha256:REPLACE_WITH_VERIFIED_DIGEST
      volumeMounts:
        - name: database-data
          mountPath: /var/lib/dispatchdesk
  volumes:
    - name: database-data
      persistentVolumeClaim:
        claimName: dispatchdesk-db-data
```

This is only a Pod spec excerpt. Replace the image digest and ensure the database's configured data directory matches the mount. A filesystem mounted over an existing directory hides the image's original contents at that path. Filesystem ownership, security context, access mode, mount options and driver behavior can prevent the process from reading or writing. Kubernetes mounting a volume successfully does not prove that the database can recover its files or that those files are valid.

PV reclaim policy determines what happens after a claim is released. Dynamically provisioned volumes inherit the StorageClass policy, which commonly defaults to `Delete`; with a supporting driver, deleting the PVC can delete the backing storage asset. `Retain` leaves the PV and asset for manual reclamation, but the old data remains and must be protected before reuse. `Recycle` is deprecated. Inspect the StorageClass and bound PV before deleting a PVC. A finalizer may delay API object deletion while the provisioner handles the external volume; that delay is not a backup. Refer to [PersistentVolumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/), [StorageClasses](https://kubernetes.io/docs/concepts/storage/storage-classes/) and [dynamic provisioning](https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/).

## StatefulSets and storage lifecycle

Use a StatefulSet when replicas need stable ordinal identity, stable network identity, or one persistent claim per replica, and when ordered creation, update or scaling helps the application protocol. A [Deployment](104-deployments-replicasets-and-jobs.md) with interchangeable stateless replicas is usually simpler if the application keeps state elsewhere. A StatefulSet does not turn arbitrary software into a replicated database or manage consensus, backup, failover or data repair. It provides identity and storage wiring; the application and storage system still define consistency and recovery. Resource fit and scheduling constraints from [Chapter 108](108-resource-requests-limits-and-scheduling.md) still apply to stateful Pods and their storage topology.

A StatefulSet uses a governing headless Service for stable network identity and `volumeClaimTemplates` to create a claim for each ordinal. For example, a set named `dispatchdesk-store` with two replicas could produce Pods `dispatchdesk-store-0` and `dispatchdesk-store-1`, and corresponding PVCs such as `data-dispatchdesk-store-0`. If a Pod is deleted and recreated, it keeps its ordinal and reuses the associated claim, even if it lands on a different node. The replacement does not receive an empty disk simply because the Pod UID changed. Whether the storage can attach in the new topology depends on the driver and the volume's zone or node constraints.

Ordered behavior is useful for some clustered databases but can impede recovery when the first ordinal never becomes Ready. `podManagementPolicy: Parallel` changes Pod creation/deletion ordering in specified operations; it does not change the application's quorum requirements or make startup safe. StatefulSet update strategy, partitioning, readiness and `minReadySeconds` also affect rollout behavior. Plan rollouts around the database's membership and replication protocol rather than treating a StatefulSet as a Deployment with persistent directories.

Claim retention deserves special attention. By default, scaling down or deleting a StatefulSet does not automatically delete its PVCs, which helps preserve data for recovery but leaves storage assets and costs behind. StatefulSets can define a PVC retention policy for deletion or scale-down; the behavior depends on the policy and cluster support. Deleting a PVC can then trigger the PV reclaim policy and permanently remove the backing storage. Before changing replica count, deleting a StatefulSet or its PVCs, inspect all claims and verify the data retention plan. Never use a broad namespace deletion as a casual cleanup for stateful labs.

Persistent storage is not the same as backup. A replicated volume or cloud disk can preserve data through Pod replacement while still sharing a failure domain with the cluster, account, region or operator mistake. A snapshot may be crash-consistent rather than application-consistent; databases often need their own backup/freeze/checkpoint procedure. Test restoring into an isolated destination, validating integrity and measuring recovery time. [Chapter 120](../12-kubernetes-production-engineering/120-upgrades-etcd-and-cluster-recovery.md) covers etcd and cluster-level recovery; [Chapter 186](../19-site-reliability-and-recovery/186-backup-engineering.md) covers workload-level backup engineering and application-data restore. Storage choices must align with those distinct recovery needs.

## Replacing a Pod without losing data

Suppose `dispatchdesk-store-0` stops responding and the team assumes deleting its PVC will force Kubernetes to create a clean replica. That assumption can destroy the only copy of the database files. First preserve evidence: inspect the StatefulSet, Pod events, claim status, bound PV, node and volume attachment state, and application logs. Determine whether the Pod process is unhealthy, the node is unavailable, attachment is stuck, or the filesystem/application has a data integrity problem. Do not delete or recreate the claim as an exploratory fix.

Read-only inspection with an explicit context and namespace might include:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  get statefulset dispatchdesk-store -o wide
kubectl --context kind-dispatchdesk --namespace production \
  get pods -l app.kubernetes.io/name=dispatchdesk-store -o wide
kubectl --context kind-dispatchdesk --namespace production \
  get pvc data-dispatchdesk-store-0 -o wide
kubectl --context kind-dispatchdesk --namespace production \
  describe pvc data-dispatchdesk-store-0
kubectl --context kind-dispatchdesk \
  get pv -o wide
```

The final command lists cluster-scoped PVs; correlate the PV's `Claim` field with the namespaced claim rather than guessing from a generated PV name. `describe` includes events that can explain a Pending claim, mount failure or provisioning delay. A Bound claim means storage is associated in the API; it does not establish that the volume is attached, writable, healthy, backed up or application-consistent. Also inspect the StatefulSet's owner and `volumeClaimTemplates`, storage class, reclaim policy and CSI events through the tools approved for the installed driver.

If the Pod object alone is damaged and the data is sound, a controller may replace the Pod while retaining the claim. Before forcing deletion, confirm whether the node is actually stopped or isolated: a partitioned old process might still write, and a replacement writer can cause split-brain or filesystem corruption. Let the storage driver detach safely and follow the database's failover procedure. If recovery uses a backup or snapshot, create a new claim or isolated restore target and validate it before directing clients to the recovered workload. Preserve the original volume until recovery is confirmed and retention requirements are satisfied.

Resizing usually means increasing a PVC request when the StorageClass and driver support expansion. Filesystem expansion may complete online or require filesystem-specific action or Pod restart. Kubernetes generally supports growing, not shrinking, a claim; do not reduce the requested capacity to work around a full disk. A full volume is an application incident: inspect database growth, logs, filesystem usage and retention, and verify backups before deleting files. Storage snapshots, clones and expansion are driver-specific capabilities and should be tested against the actual platform.

## Exercises and answer guidance

1. A PVC is Pending, while nodes show free memory and CPU. What else should be checked? StorageClass/provisioner availability, PV matching, access mode/capacity, topology, quota and PVC events; compute headroom does not provision a disk.
2. A StatefulSet Pod is deleted but the replacement sees the same data. Why? The ordinal identity remains and the Pod reuses its per-ordinal PVC; a new Pod UID does not imply new persistent storage.
3. Does `ReadWriteOnce` guarantee only one Pod can write to a volume? No. It generally constrains read-write mounting to one node; multiple Pods on that node may still use it, subject to driver and application behavior.
4. A team deletes a PVC whose PV policy is `Delete`. What might happen? The provisioner can delete both the Kubernetes PV and backing storage asset; inspect reclaim policy and preserve/backup data first.
5. A disk is full and someone proposes reducing a 100Gi PVC to 50Gi. Is that a supported recovery? No, PVC expansion supports growth rather than shrink; diagnose usage, add capacity where supported and apply data-retention or recovery plans.

Review questions: how do PVC, PV and StorageClass relate, what identity does a StatefulSet preserve, what does reclaim policy control, and what evidence is required before replacing or deleting storage?

## Verification and primary sources

Official Kubernetes PersistentVolume, StorageClass, dynamic provisioning, StatefulSet and PVC expansion documentation was inspected on 2026-10-04. PVC, Pod and StatefulSet fragments are illustrative; no storage class, claim, volume, database or Pod was created or deleted. Creating a PVC may allocate billable external storage. Static checks do not establish the cluster provisioner, reclaim behavior, volume topology, access semantics, backup consistency, filesystem expansion or database recovery.

Primary references: [PersistentVolumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/), [StorageClasses](https://kubernetes.io/docs/concepts/storage/storage-classes/), [dynamic provisioning](https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/), [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/), and [resizing persistent volume claims](https://kubernetes.io/docs/tasks/configure-pod-container/resize-persistent-volume-claim/).
