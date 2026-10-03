---
book: The Complete DevOps Engineering Book
volume: 6
volume_title: "Docker in Practice"
chapter: 56
title: "Docker Volumes and Persistent Data"
slug: docker-volumes-and-persistent-data
status: complete
summary: ../../_ai/chapter-summaries/056-docker-volumes-and-persistent-data.md
---

# Chapter 56 — Docker Volumes and Persistent Data

Replacing a container should replace its process and filesystem layer, not erase DispatchDesk orders. A container's writable layer belongs to that particular container. When it is removed, data written there is removed with it. Persistent data needs an explicit storage location and recovery procedure. A mount gives a process access to storage outside that writable layer; it does not by itself make the data backed up, consistent, encrypted, or available from another host.

The examples assume a Linux Docker Engine on a disposable host and an operator authorized to use its intended local daemon. Docker commands act on the daemon selected by the current context, which may be remote; paths in a bind mount are resolved on the daemon host. Do not use a production database directory for the lab. For the container filesystem distinction, see [Chapter 45](../05-container-internals-and-oci/045-container-filesystems-and-storage.md); this chapter focuses on where mounted data lives and how to retain it through replacement.

## Volumes, bind mounts and ownership

A Docker volume is a named storage object managed through the Docker daemon. Its contents live outside a container's writable layer, and multiple containers can mount it. A named volume is a good default for application data when the Docker host owns the data lifecycle. Docker manages the volume's host path, reducing direct dependence on a particular filesystem location. A volume can still be lost with its backing disk, host, account or operator mistake; volume management is not a backup service.

A bind mount maps a specific path from the daemon host into the container. Use it when the host path itself is part of the contract: a developer wants live source edits, an operator supplies a configuration file, or a host agent needs access to a directory. The daemon host must have the path, and the container process receives the host path's permissions and contents. Bind mounts tie a container to host layout and can expose sensitive host files if the mount is broader than needed. Docker Desktop mediates these paths through its Linux VM; remote Docker contexts resolve source paths remotely.

The `--mount` form makes source and destination explicit. This command creates a new named volume and mounts it at `/var/lib/dispatchdesk` in a disposable container:

```bash
docker volume create dispatchdesk-data
docker run --detach --name dispatchdesk-data-check \
  --mount type=volume,source=dispatchdesk-data,target=/var/lib/dispatchdesk \
  alpine:3.20 sleep 1d
```

Run it on a disposable Docker host. The tag is a learning example, not an immutable production identity; production deployment should pin and verify the intended image digest. The command downloads the image if needed, creates local daemon objects and starts a process, but publishes no port. `sleep 1d` keeps the process available for inspection; it is not an application server. The volume is created explicitly first, which lets the operator distinguish it from the container and avoid relying on an automatically generated anonymous volume name.

Put a harmless marker in the example volume so replacement and restore can be verified with content, not only mount metadata:

```bash
docker run --rm \
  --mount type=volume,source=dispatchdesk-data,target=/data \
  alpine:3.20 sh -c 'printf "%s\\n" "dispatchdesk-lab-record-001" > /data/marker.txt'
```

Inspect the attachment and volume metadata:

```bash
docker inspect dispatchdesk-data-check \
  --format '{{json .Mounts}}'
docker volume inspect dispatchdesk-data
```

The mount record should identify a volume source named `dispatchdesk-data` and the target `/var/lib/dispatchdesk`. A named volume persists independently of the container lifecycle. Docker may populate an empty volume with image contents already present at the mount destination; `volume-nocopy` disables that initial copy. A nonempty volume obscures files that the image contains at that destination. This matters when a new image version changes default files: attaching old state does not merge it with the image directory. Check the application's upgrade procedure before treating an image update as a data migration.

Bind mounts are often clearer for source trees and host-managed config. On a disposable Linux Docker host, create an empty path and mount it read-only:

```bash
mkdir -p "$PWD/dispatchdesk-config"
docker run --rm \
  --mount "type=bind,source=$PWD/dispatchdesk-config,target=/etc/dispatchdesk,readonly" \
  alpine:3.20 ls -la /etc/dispatchdesk
```

Here `$PWD` is expanded by the shell on the CLI machine. With a local Linux daemon that is the host filesystem path; with a remote daemon the path must exist on the remote host, and a local relative path will not magically transfer files. `readonly` prevents writes through this mount but does not make a writable parent path or other mounts read-only. The empty directory intentionally masks the image's `/etc/dispatchdesk` contents. If the directory is missing, `--mount` typically reports an error instead of silently creating it; exact behavior should be checked for the Engine in use. Docker Desktop shares permitted local paths into its VM.

On Fedora/RHEL with SELinux enforcing, a bind mount may be denied even when Unix mode bits look permissive because the host label is not accessible to the container domain. For this disposable, dedicated lab directory, `-v` syntax can request a private container label; the `:Z` option is not available on `--mount`:

```bash
docker run --rm \
  -v "$PWD/dispatchdesk-config:/etc/dispatchdesk:ro,Z" \
  alpine:3.20 ls -la /etc/dispatchdesk
```

Use `:Z` only for a dedicated path that should be relabeled privately for one container. Lowercase `:z` requests a shared label for a path intentionally used by multiple containers; do not switch to it merely to make an access error disappear. Relabeling changes host extended attributes and can make a path unsuitable for other host services; never apply either option casually to a broad system directory or shared content. Docker SELinux behavior depends on the Engine and policy. Rootless configurations also map UIDs/GIDs, so verify access as the actual container identity rather than disabling enforcement.

Mount choice does not solve Unix ownership. A process running as UID 10001 inside a container normally accesses files according to that identity as interpreted by the daemon and host filesystem. Rootless Docker and user-namespace remapping translate identities; the host-visible UID may differ from the container UID. A database image may initialize an empty volume with its expected ownership, while a pre-populated bind directory can retain incompatible ownership. Before changing ownership recursively, inspect the actual image user, mount source, user-namespace configuration and application expectations. `chmod -R 777` removes useful boundaries and can create security problems; it is not a general permission repair.

Choose storage based on the data contract. Use the container layer for disposable caches or generated files that can be recomputed. Use a named volume for daemon-managed persistent state on one host. Use a bind mount for deliberately host-owned files or development workflows. If the workload must move across hosts, survive host loss or meet a recovery objective, choose and test a storage and replication design for that requirement; the word “volume” alone promises none of these properties.

## Backup and database consistency

Back up a named volume by reading it to an archive from a helper container. This illustrates local file capture, not a complete disaster-recovery plan. Run on a disposable host with enough disk space and a destination directory you control. The application should be stopped or placed in its documented quiescent mode first if it writes the volume; a tar archive of active mutable files can contain a mixture of states.

```bash
mkdir -p "$PWD/backups"
docker stop dispatchdesk-data-check
docker run --rm \
  --mount type=volume,source=dispatchdesk-data,target=/source,readonly \
  --mount "type=bind,source=$PWD/backups,target=/backup" \
  alpine:3.20 sh -c 'tar -C /source -czf /backup/dispatchdesk-data.tgz .'
sha256sum "$PWD/backups/dispatchdesk-data.tgz"
```

The helper sees the source volume read-only and writes the archive through the bind mount to the daemon host's `backups` directory. On Fedora/RHEL with SELinux enforcing, replace the second `--mount` with `-v "$PWD/backups:/backup:Z"` and use only this dedicated lab directory; the `:Z` behavior and host relabeling caveat described above apply. On a remote context, the destination belongs to the remote daemon host, not necessarily the machine running the CLI. The checksum detects some later accidental changes but does not prove the archive contains the right files or can be restored. Keep copies off the host and outside the Docker daemon's ordinary deletion boundary, protect access and encryption keys, define retention, and rehearse restore. A second directory on the same disk is not an off-host backup. Stopping the example container protects only this toy process; stopping a real service may cause downtime and should follow its maintenance process.

Restore the archive into a new, isolated named volume and compare the marker. First refuse to reuse a volume of the same name so the target is known to be fresh:

```bash
if docker volume inspect dispatchdesk-restore-check >/dev/null 2>&1; then
  printf '%s\n' 'Refusing to reuse existing volume dispatchdesk-restore-check' >&2
  exit 1
fi
docker volume create dispatchdesk-restore-check
docker run --rm \
  --mount type=volume,source=dispatchdesk-restore-check,target=/restore \
  --mount "type=bind,source=$PWD/backups,target=/backup,readonly" \
  alpine:3.20 sh -c 'tar -C /restore -xzf /backup/dispatchdesk-data.tgz'
docker run --rm \
  --mount type=volume,source=dispatchdesk-restore-check,target=/restored,readonly \
  alpine:3.20 sh -c 'test "$(cat /restored/marker.txt)" = "dispatchdesk-lab-record-001" && sha256sum /restored/marker.txt'
```

Tar extraction can overwrite files with matching paths in its destination. Here the preflight refuses an existing volume and extraction runs only in the fresh `dispatchdesk-restore-check` volume; it cannot modify the source volume or another host directory. This verifies that the archive is readable and includes the expected sample file, but does not prove production data consistency or off-host recoverability. On Fedora/RHEL with SELinux enforcing, use a dedicated `-v "$PWD/backups:/backup:ro,Z"` bind mount for the restore helper too. Compare the reported checksum with the source marker if you record it before backup. Delete the restore-check volume only after the comparison succeeds.

For PostgreSQL, treat the Docker volume as a storage location, not as a backup format. Copying a running database's data directory with `tar` or a host snapshot can capture files from different points in a transaction and is not automatically a valid backup. Use PostgreSQL's supported backup methods: `pg_dump` for a consistent logical snapshot of one database, `pg_dumpall` for cluster-wide global objects, or base backup plus WAL archiving for physical recovery and point-in-time objectives. These methods have different RPO, restore-time and version requirements. See [Chapter 36](../04-vps-and-server-operations/036-database-and-cache-operations-on-one-host.md) and [Chapter 37](../04-vps-and-server-operations/037-server-backups-and-restore.md) for the broader recovery plan. A consistent logical dump still needs secure off-host storage and an exercised restore; it does not capture the Docker host, roles in every configuration, secrets, or application deployment by itself.

Application consistency also spans services. If an API writes a database row and an uploaded file as related operations, a database dump and a volume archive taken at different times may represent different application states. Define whether uploads can be reconciled, pause or coordinate writes, record a cutover point, and test invariants after restoring both. For PostgreSQL WAL archiving or physical backups, follow the chosen tool's documented coordination procedure rather than adding an independent filesystem copy.

## Surviving container replacement

The volume lifecycle is independent of a container's lifecycle. Demonstrate that boundary by removing the stopped lab container and creating a replacement against the same named volume:

```bash
docker rm dispatchdesk-data-check
docker run --detach --name dispatchdesk-data-replacement \
  --mount type=volume,source=dispatchdesk-data,target=/var/lib/dispatchdesk \
  alpine:3.20 sleep 1d
docker inspect dispatchdesk-data-replacement \
  --format '{{range .Mounts}}{{.Name}} -> {{.Destination}}{{end}}'
docker exec dispatchdesk-data-replacement cat /var/lib/dispatchdesk/marker.txt
```

The new container should reference `dispatchdesk-data` at the same destination, and the final command should print `dispatchdesk-lab-record-001`. In a real stateful service, verify data through the application's supported query or health path; `docker inspect` proves the mount is configured, not that the application can read or interpret its contents. An image upgrade can change schemas, UID expectations or directory layout. Keep a tested data migration and rollback plan, and do not assume that starting the old image against already migrated data is safe.

Anonymous and named volumes have different cleanup behavior. `docker run --rm` removes its container and its associated anonymous volumes, but named volumes persist. `docker rm -v` can remove anonymous volumes associated with a container; it does not remove explicitly named volumes. `docker volume rm dispatchdesk-data` explicitly deletes the named volume and its data and normally fails while a container still uses it. In Docker's current volume-prune behavior, `docker volume prune` removes unused anonymous volumes by default; `docker volume prune --all` includes unused named volumes and requires API 1.42 or later. “Unused” means no container references the volume, including stopped containers. Pruning can still delete data whose container was removed accidentally. Before removing storage, list and inspect candidates, identify the owning application, verify a recoverable backup, and obtain the change authorization required by that environment. This disposable lab uses explicit `docker volume rm` for its two named volumes and does not run prune.

If the replacement starts with an empty directory, first check that it uses the intended Docker context and volume name. A successful `docker run` against another daemon can create a fresh volume with the same spelling. Then inspect mounts, confirm the application expects the target directory, and check its logs and effective UID/GID. A volume created under one Compose project or daemon is not automatically the volume used by another. If the path contains data but the process reports permission denied, inspect numeric ownership and user mapping before changing it. If the files exist but the application reports an invalid or old schema, restore into an isolated volume and use the database's migration or recovery procedure; never test repair commands against the only copy.

Once replacement is verified, remove the toy container and volume only from the disposable daemon:

```bash
docker stop dispatchdesk-data-replacement
docker rm dispatchdesk-data-replacement
docker volume rm dispatchdesk-data
docker volume rm dispatchdesk-restore-check
rm -f "$PWD/backups/dispatchdesk-data.tgz"
rmdir "$PWD/backups" "$PWD/dispatchdesk-config" 2>/dev/null || true
```

The final volume removals permanently discard the lab's local data. Do not copy this cleanup sequence into a production runbook without confirming the daemon, volume identity, backup and deletion approval. The `rmdir` command removes only empty directories; if unrelated files remain, it leaves them in place. `|| true` prevents a nonempty or absent lab directory from stopping cleanup, but should not be used to hide errors in a production deletion workflow.

## Exercises and review questions

1. A developer recreates an API container and loses uploaded files. What storage choice would retain files across container replacement, and what additional failure does that choice still not protect against?
2. The CLI reports a volume named `dispatchdesk-data`, yet the replacement sees an empty directory. List the first checks that distinguish a new volume from missing files or a permissions problem.
3. When would a bind mount be a better fit than a named volume? State one benefit and one operational coupling it introduces.
4. Why is a tar archive of a live PostgreSQL data volume not automatically a valid database backup? Name two supported recovery approaches and the kinds of objectives they can serve.
5. A database and upload volume are archived an hour apart while users continue to write. Which consistency problem can occur, and how might the restore plan handle it?
6. Which objects does `docker run --rm` remove when the container used an anonymous volume and a named volume?

### Answer guidance

1. Mount uploads on a named volume to survive replacement on that daemon. It still shares the host's disk and failure boundary unless a separate backup or storage design covers host loss.
2. Confirm the active context and daemon host; inspect the container's mount source and target; inspect the named volume; then check numeric ownership, user mapping and application logs. Similar volume names on different daemons are independent objects.
3. A bind mount fits when the host must manage or edit the files directly. It couples deployment to a host path, its permissions and its availability on the daemon host.
4. Files can be copied at inconsistent moments while transactions are changing. `pg_dump` provides a logical database snapshot; base backup with WAL archiving can support physical recovery and point-in-time goals. Both require a tested restore and off-host protection.
5. Related rows and files may represent different application moments, leaving orphan records or missing content. Coordinate a quiet window or write pause, capture a shared cutover point, and run reconciliation checks after restore.
6. `--rm` removes the container and associated anonymous volumes. Named volumes are independent and remain until explicitly removed or pruned as unused.

## Takeaways

- Container writable layers follow the container lifecycle; mounts place files in separate storage with a separate lifecycle.
- Named volumes are managed by a Docker daemon; bind mounts expose a path on that daemon's host.
- Storage persistence across container replacement does not imply host resilience, application consistency or recoverability.
- Match ownership and user mapping to the process identity; inspect before repairing permissions.
- Use database-supported backup procedures for databases, protect copies beyond the host failure boundary and prove recovery with rehearsals.
- Confirm the current daemon and storage identity before replacing or deleting state.

## Further reading

- [Docker networking](055-docker-networking.md) — daemon contexts and container boundaries.
- [Docker Compose for Multi-service Applications](057-docker-compose-for-multi-service-applications.md) — declaring volumes with an application stack.
- [Container Filesystems and Storage](../05-container-internals-and-oci/045-container-filesystems-and-storage.md) — image and writable-layer behavior.
- [Server Backups and Restore](../04-vps-and-server-operations/037-server-backups-and-restore.md) — recovery objectives, off-host copies and restore drills.

## Sources and verification

Docker's [storage overview](https://docs.docker.com/engine/storage/), [volume](https://docs.docker.com/engine/storage/volumes/), [bind mount](https://docs.docker.com/engine/storage/bind-mounts/) and [volume prune](https://docs.docker.com/reference/cli/docker/volume/prune/) documentation and PostgreSQL 18's [backup overview](https://www.postgresql.org/docs/current/backup.html), [`pg_dump`](https://www.postgresql.org/docs/current/app-pgdump.html) and [`pg_basebackup`](https://www.postgresql.org/docs/current/app-pgbasebackup.html) documentation were inspected on 2026-10-03. Version-sensitive Docker storage lifecycle statements reflect that inspection date; consult the deployed Engine and database versions. Commands are reader-run examples and were not executed because no Docker daemon or database is available in this workspace. The local tar procedure is illustrative file capture only and is not a database backup method.
