---
book: The Complete DevOps Engineering Book
volume: 5
volume_title: "Container Internals and OCI"
chapter: 45
title: "Container Filesystems and Storage"
slug: container-filesystems-and-storage
status: complete
summary: ../../_ai/chapter-summaries/045-container-filesystems-and-storage.md
---

# Chapter 45 — Container Filesystems and Storage

## Follow a write to its storage owner

A container presents one root filesystem, but its visible files can come from several places: read-only image layers, a container-specific writable layer, a named volume, a bind mount, a tmpfs mount or a network-backed filesystem. The path visible to the application does not reveal who owns the data or how long it survives. DispatchDesk's orders must remain durable when the API container is replaced, so the database path cannot accidentally live only in the container's writable layer.

The Open Container Initiative describes image layers as ordered filesystem changesets. Linux OverlayFS can combine lower and upper directory trees into a merged view. When a process first modifies a lower-layer file, OverlayFS may copy it up into the upper tree; deletions are represented so the lower path stays hidden. The application sees a normal path, while the storage implementation tracks the change separately.

Copy-on-write can make image distribution efficient, but a write to a large existing file may require copying that file into the writable layer. Storage-driver behavior and cost differ. Do not place write-intensive databases in a container layer just because the path is writable. Use a deliberately managed data mount and validate its latency, ownership, backup and recovery behavior.

## Choose a mount by its lifecycle

| Storage type | Typical owner and lifecycle | Common use | Main operational question |
|---|---|---|---|
| Image lower layers | Image and runtime storage | Read-only application files | Which digest and platform created these bytes? |
| Container writable layer | One container instance; often removed with it | Temporary application output | Can every write be discarded when the instance is replaced? |
| Named volume | Container engine on a host, independent of a single container | Persistent or shared files | Who backs it up, migrates it and restores it on another host? |
| Bind mount | A specific host path projected into the container | Explicit host integration or development source | Does the host path exist with safe ownership and access? |
| tmpfs | Memory-backed temporary filesystem | Ephemeral scratch data or selected secrets | Is the content expected to vanish at stop or reboot, is memory bounded, and could pages be swapped to persistent storage? |
| Network filesystem | External storage service or server | Shared files with a network lifecycle | What are its consistency, availability, latency and credential contracts? |

A tmpfs can keep scratch data out of the container's image and writable layers, but its pages may be swapped to persistent storage. “Memory-backed” therefore does not guarantee that sensitive bytes never reach disk. Bound its size, use the host's approved swap-encryption and secret-management policy, and consider whether the workload can avoid writing sensitive material to temporary files at all.

A named volume is more independent of an individual container than its writable layer, but it is not automatically independent of the engine host. If that VPS is lost, the volume may be lost with it unless a separate backup or replication system protects it. A bind mount can provide an explicit path and make host backup easier, but it exposes the container to host files under the mount and couples deployment to host path layout. Read-only mounts reduce write capability where the workload permits it.

Tmpfs is useful when data must not persist to the container's normal storage, but it consumes host memory and disappears according to mount lifecycle. Avoid placing large payloads or durable order state there. Network filesystems introduce their own failure and locking semantics; confirm that the database or application explicitly supports the chosen filesystem rather than assuming a mounted directory behaves like a local disk.

## Protect persistent application data

DispatchDesk's API can be replaced without losing an order only when the authoritative database is outside the API container's disposable layer. PostgreSQL can run in another container for a local lab, on a separately managed host or as a managed service; its storage lifecycle still requires a supported database backup and restore. An engine volume may preserve files when a database container is recreated, but volume persistence alone does not create a consistent backup, encryption policy, off-host copy or point-in-time recovery.

For production database files, consider a supported host or managed service before placing the data directory in a container-managed overlay. If using a volume, the database vendor's instructions, storage class, filesystem semantics, owner mapping and backup tooling still apply. Quiesce or use the database's own online backup interface; do not tar a live data directory and label it restorable without a consistency guarantee. See [Chapter 36](../04-vps-and-server-operations/036-database-and-cache-operations-on-one-host.md) and [Chapter 37](../04-vps-and-server-operations/037-server-backups-and-restore.md).

A multi-writer mount can create corruption or stale reads if the application expects exclusive local-file semantics. Shared access must follow an application or database concurrency protocol. Two containers mounting the same data does not make them a safe replicated database. Likewise, a volume attached to one VM may not be attachable to another at the same time; check the storage service's constraints and failure behavior.

## Inspect mounts and capacity

For a container you own or are authorized to inspect, the engine can report the configured mounts:

```bash
docker inspect --format '{{json .Mounts}}' CONTAINER_NAME
docker inspect --format '{{.GraphDriver.Name}}' CONTAINER_NAME
```

These are read-only inspection commands for Docker. Replace `CONTAINER_NAME` with a known test container. The `GraphDriver` field may be absent or uninformative when a newer Docker installation uses a containerd image store; inspect the engine's version and storage configuration rather than assuming `overlay2`. A named volume's host path is implementation detail and should not be edited directly while the engine owns it.

Then inspect the underlying mount and free capacity using authorized host tools:

```bash
findmnt
df -h
df -i
```

Check the filesystem that actually holds the data, not only the container's apparent root. Watch bytes, inodes, thin-pool capacity where applicable, volume quota, backend capacity, latency and backup staging. Container log files may also consume engine storage. Configure log retention and monitor the engine's storage root according to its own documentation.

Host filesystem commands such as `findmnt` and `df` must run on the host that owns the engine's storage. With a remote Docker context, running them on the CLI client inspects the client's filesystems, not the daemon host; connect through the authorized host-management path before drawing conclusions. Docker storage details change across releases. Docker Engine 29 and later uses a containerd image store by default for fresh installations, which uses snapshotters rather than the classic `overlay2` storage-driver path. Existing installations may retain another storage mode. The general layering and persistence concepts still apply, but commands and directory layouts differ. Podman and other engines also use their own storage configuration and rootless paths. Record the actual runtime and storage backend before troubleshooting disk use.

## Plan data migration deliberately

Moving data between hosts requires an application-consistent copy and an explicit cutover. For a database, use its supported backup, replication or migration method. For static files, compare content and metadata, preserve ownership and ACLs where required, and define how writes are paused or synchronized during the final copy. Keep the previous source intact until the destination passes integrity checks and the application is reading and writing through the intended path.

Before deleting a volume, identify every container and service that references it, the backup state, retention requirement and rollback point. Engine cleanup commands can remove unused objects based on engine bookkeeping; “unused” does not mean “unneeded.” Avoid broad prune commands on hosts holding operational state unless the exact deletion scope is known and approved by the host's change process.

## Exercises and review questions

1. DispatchDesk's API container is replaced and its local `orders.db` disappears. Which storage choice caused the loss, and what authority should own accepted orders?
2. A process modifies a 2 GiB file from an image layer. What might copy-on-write do, and why can a writable layer grow unexpectedly?
3. Compare a named volume with a bind mount for portability, host coupling, access control and backups.
4. The engine reports ample container-root space but a mounted volume is full. Which filesystem and quota should you inspect?
5. A team wants two database containers to mount the same directory for availability. Which concurrency and failure guarantees are missing from that plan?

**Answer guidance:** For exercise 1, the file lived only in the disposable container writable layer; accepted orders belong in an external database or deliberately managed persistent authority with tested backups. For exercise 2, a first write to a lower-layer file may copy the file into the upper writable layer, so the changed copy and other generated data can consume more space than the small logical edit suggests; use actual backend metrics. For exercise 3, a named volume is engine-managed and easier to preserve across container replacement but remains host/engine-specific; a bind mount names a host path and exposes host ownership/ACL/LSM policy directly. Both need explicit backup, migration and restore plans. For exercise 4, identify the mounted host/backend filesystem, quota or storage class and the actual daemon host; with a remote engine, client-local `df` is the wrong observation point. For exercise 5, shared filesystems do not supply database locking semantics, write fencing, replication, leader election, consistent recovery or split-brain prevention; use the database's supported HA protocol.

Follow data through the actual mount and storage implementation before choosing a backup or migration procedure. Next, [OCI Runtimes and Container Engines](046-oci-runtimes-and-container-engines.md) explains how a user-facing engine coordinates the image, storage and process lifecycle.

## Sources and verification

The Linux kernel's [OverlayFS documentation](https://docs.kernel.org/filesystems/overlayfs.html), OCI image and runtime specifications, and Docker's [storage-driver](https://docs.docker.com/engine/storage/drivers/), [volume](https://docs.docker.com/engine/storage/volumes/) and [containerd image-store](https://docs.docker.com/engine/storage/containerd/) documentation were inspected on 2026-10-04. Docker's containerd image-store default in Engine 29 is called out as version-sensitive. Inspection commands passed shell syntax checks but no container or volume was inspected or changed.
