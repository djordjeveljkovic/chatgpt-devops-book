---
book: The Complete DevOps Engineering Book
volume: 4
volume_title: "VPS and Server Operations"
chapter: 36
title: "Database and Cache Operations on One Host"
slug: database-and-cache-operations-on-one-host
status: complete
summary: ../../_ai/chapter-summaries/036-database-and-cache-operations-on-one-host.md
---

# Chapter 36 — Database and Cache Operations on One Host

## A shared host creates shared limits

Putting the application, PostgreSQL and Redis on one VPS can reduce early infrastructure cost and simplify networking. It also places their CPU, memory, disk latency, file descriptors and failure domain on one machine. A query spike can slow API requests; a cache eviction policy can consume memory needed by the database; a full filesystem can stop both services. Local placement makes a network path shorter, not the system independent or automatically safe.

For this Harbor scenario, PostgreSQL owns accepted orders and notification intent. The application must preserve the Chapter 10 invariant by committing both records together before acknowledging acceptance. Redis is an optional cache for reconstructible results. It is not the authority for orders, pending notifications, locks whose loss would break correctness, or retry state. If cache loss changes whether an order exists or whether work is delivered, it is no longer merely a cache and needs a separate contract.

Choose the database and cache packages for a named distribution release instead of assuming their names or service units match. On Ubuntu Server 24.04, the distribution packages are `postgresql`, `postgresql-client` and `redis-server`; install them only after reviewing the repository and maintenance plan. `postgresql.service` may report the cluster-manager unit rather than prove a particular cluster is ready. Use `pg_lsclusters` to identify the actual version/name/port and inspect its `postgresql@<version>-<cluster>.service` unit. On Fedora 42, PostgreSQL is packaged as `postgresql-server` and `postgresql`; the server requires the release's documented one-time initialization before its `postgresql.service` is useful, and Fedora's cache-compatible service may be Valkey. On RHEL 9, confirm entitlement and AppStream access, inspect `dnf module list postgresql` and `dnf module list redis`, and select a supported stream; releases may also provide Valkey. Never silently substitute Redis and Valkey for a compatibility promise without testing the client protocol and behavior. Check `dnf list postgresql-server redis valkey` and `systemctl list-unit-files 'postgresql*' 'redis*' 'valkey*'` on the actual host. Before changing a live host, record installed versions, configuration source, active service state, data directory, backup status and available disk. Avoid copying a data directory between major PostgreSQL versions; use the supported upgrade or logical migration process for that version.

For example, the Ubuntu cluster inventory and service checks are:

```bash
pg_lsclusters
systemctl list-units --type=service 'postgresql*'
systemctl is-active postgresql@16-main.service
sudo -u postgres pg_isready -h /var/run/postgresql -p 5432
```

The `16-main` name and port are examples; use the values reported by `pg_lsclusters`. For a modular RHEL installation, first inspect the selected cluster and unit files instead of assuming the Ubuntu cluster-unit naming convention. An active umbrella unit is not proof that the intended cluster accepts connections.

## Keep the data services private

PostgreSQL should accept local connections only unless there is a documented need for remote access. Its `listen_addresses` setting controls network interfaces; client authentication rules are a separate decision. A narrow host binding and an authentication rule complement each other. Unix-domain sockets can avoid TCP when the application and database share a host and the chosen driver supports the intended socket path.

Inspect active configuration instead of assuming a package default:

```bash
sudo ss -ltnp
sudo -u postgres psql -X -c 'SHOW listen_addresses;'
sudo -u postgres psql -X -c 'SHOW hba_file;'
sudo -u postgres psql -X -c 'SHOW data_directory;'
```

These commands reveal PostgreSQL settings and paths on a system where the `postgres` OS account and `psql` are available. A value of `*` can expose a listener on every suitable interface; it does not by itself say who can authenticate. Review the effective `pg_hba.conf` rules in order and use a modern password method such as SCRAM when password authentication is selected. Create a least-privilege application role limited to the application database and required schema operations. Do not run the web process as the PostgreSQL superuser or OS account.

Redis is designed for trusted clients. On a single-host deployment, bind it to loopback or a protected Unix socket and deny public access at both provider and host firewalls. Do not treat Redis protected mode as a firewall or as authorization. Use ACL users with only required keys and commands when the application needs authenticated access. Keep credentials out of command arguments, shell history and world-readable environment files. Restrict access to the Redis socket and configuration according to the application's actual identity.

Confirm what is reachable after any change:

```bash
sudo ss -ltnp | rg ':(5432|6379)\b'
sudo ss -lxnp | rg '(postgres|redis)'
```

A missing TCP listener may be intentional if a Unix socket is in use. Conversely, a loopback TCP listener is private to the host network namespace but still accessible by local processes permitted by host policy. A container or another namespace may have a different view. Validate the actual application path and external exposure separately.

## Bound connections and memory together

Do not tune PostgreSQL `max_connections` by multiplying an arbitrary per-process pool size. Every web worker, background worker, migration process, monitoring check and operator session can consume a connection. More PostgreSQL connections use more resources, and query memory can multiply across concurrent operations. A larger `work_mem` is not a global cap: multiple sorts or hashes in one query and multiple active sessions can each use memory. Redis also holds data and client buffers in memory. The Linux page cache is useful to PostgreSQL, but it is not spare memory that may be promised independently to every process.

Start with a capacity budget and measurements rather than a generic tuning file. Record steady and peak resident memory, swap activity, CPU saturation, database connection count, query latency, cache memory and evictions, disk free space, I/O latency and application queueing. Leave headroom for kernel memory, backups, package operations and recovery. A host without swap can still run out of memory; swap can prevent immediate termination but may turn memory pressure into severe latency. Neither setting removes the need to size the workload.

Pool application connections with a bounded maximum and queue timeout. Account for the sum across all service replicas and workers. If the total demand approaches the database limit, reduce pools, bound worker concurrency or introduce a pooler after evaluating transaction and session semantics. Do not increase the database limit without checking memory and workload effects. Alert on saturation before connection exhaustion prevents operators from connecting to diagnose it.

Redis eviction is a policy decision, not a generic fix for memory pressure. For disposable cache data, a bounded memory policy may evict keys and force the application to rebuild them. Test that behavior and make cache misses safe. For state that must persist, eviction or restart loss can violate correctness; store it in a system with the required durability and recovery contract. Redis persistence modes, write patterns and recovery time trade off memory snapshots, append-only logs and disk use. Choose based on data value and tested recovery objectives.

## Persistence and recovery must be demonstrated

PostgreSQL supports logical dumps, filesystem-level backups and continuous archiving for point-in-time recovery. They have different consistency and recovery properties. A copied live data directory is not automatically a valid backup. An off-host copy protects against VPS loss; a snapshot on the same provider account may still share deletion or account failure risks. Define recovery point and recovery time objectives, retention, encryption, access control and who tests restoration.

A logical dump is useful for selected database objects and portable restoration, but its completion is not proof that a whole service can recover within its target. For a small application database, this bounded example stages one custom-format dump on a protected local directory before the file backup in Chapter 37 sends it off-host. It assumes a current PostgreSQL client, an existing `dispatchdesk` database, local peer authentication for the `postgres` OS account and an operator-approved schedule. `pg_dump` produces a transaction-consistent view while the database remains in use; it backs up one database, not cluster-wide roles or tablespaces. Its client major version must be at least the server major version, and restore compatibility still depends on the destination version and extensions.

```bash
sudo install -d -o postgres -g postgres -m 0700 /var/backups/dispatchdesk
backup_id=$(date -u +%Y%m%dT%H%M%SZ)
sudo -u postgres pg_dump --format=custom \
  --file="/var/backups/dispatchdesk/dispatchdesk-${backup_id}.dump" \
  dispatchdesk
sudo -u postgres pg_restore --list \
  "/var/backups/dispatchdesk/dispatchdesk-${backup_id}.dump" >/dev/null
```

The directory mode limits local access; after the dump succeeds, copy it into the protected Restic selection and verify that it appears in an off-host snapshot. Check the command status and stderr, filename timestamp and database identity; a zero exit code and archive listing catch different classes of failure. Do not pipe through a command that hides `pg_dump`'s status. Do not add production credentials to command-line flags. The sample relies on local peer authentication; remote connections need a separately protected credential method.

To rehearse restoration, create a new empty database in an isolated PostgreSQL cluster or disposable host, then restore as a role permitted to create the objects:

```bash
sudo -u postgres createdb --template=template0 dispatchdesk_restore
sudo -u postgres pg_restore --exit-on-error \
  --no-owner --no-acl \
  --dbname=dispatchdesk_restore \
  /var/backups/dispatchdesk/dispatchdesk-REPLACE_WITH_REVIEWED_ID.dump
```

Use a separate target: restoring over the live database can replace or duplicate production state. Recreate reviewed extensions and grants through the deployment procedure, run schema and application checks, and submit a synthetic order only in the isolated test. Verify both retrieval and the application's actual order-to-notification-intent invariant. A logical dump does not by itself provide point-in-time recovery between dump intervals; use base backups plus continuous WAL archiving when the required RPO demands it.

Redis persistence should match its role. If Redis contains only derived cache entries, the application should tolerate an empty cache after restart and safely repopulate it. Disabling persistence may be reasonable after verifying that assumption and accepting cold-cache load. If Redis holds authoritative or queued work, explicitly select and test persistence, replication and recovery behavior; an RDB snapshot or append-only file alone does not provide off-host backup or high availability. See [Chapter 163](../17-distributed-systems-and-data-operations/163-queues-and-backpressure.md) for durable queue ownership and delivery semantics.

Disk planning includes database files, write-ahead logs, temporary query files, Redis persistence files if enabled, logs, package cache and backup staging. Keep backup output off the only filesystem being protected where possible. Monitor bytes and inodes; reserve room for WAL growth and maintenance. A full volume can prevent database writes and make recovery harder. Do not delete unfamiliar files under PostgreSQL's data directory or remove WAL files manually. Preserve evidence and use the database's documented recovery procedures.

## A read-only operational check

The following checks observe service state without changing database contents. Run them as an authorized operator using the host's actual service names and database role policy:

```bash
systemctl is-active postgresql
systemctl is-active redis-server
sudo -u postgres pg_isready
sudo -u postgres psql -X -c \
  "SELECT datname, numbackends FROM pg_stat_database ORDER BY datname;"
redis-cli -h 127.0.0.1 PING
redis-cli -h 127.0.0.1 INFO memory
df -h /var/lib /var/log
free -h
```

Ubuntu's cluster manager, Fedora/RHEL package streams and Redis-compatible cache packages can use different unit names. Discover the actual service and selected PostgreSQL cluster instead of treating `systemctl is-active postgresql` as a data-health check. `pg_isready` reports connection acceptance, not successful application authentication or query health. The statistics query exposes database-level backend counts, subject to the observing role's permissions. For a view of other users' full activity, use a dedicated monitoring login and have a DBA grant PostgreSQL's predefined `pg_monitor` role only after reviewing its broader statistics/configuration visibility; do not grant it to the application role. A Redis-compatible `PING` confirms a response but not successful ACL authentication, key availability or application behavior. With ACLs enabled, use a named least-privilege user through a protected credential mechanism; distinguish `NOAUTH`/`WRONGPASS` from a successful `PONG`. `INFO memory` may expose operational details and should be handled according to access policy. Compare outputs over time and against the service's own latency and error metrics.

For an end-to-end acceptance test in a staging environment, submit a synthetic order through the application, retrieve it using a new request, and verify its pending intent in PostgreSQL. Restarting a database or clearing a cache is not part of this read-only check. Any recovery rehearsal should use an isolated destination and a written plan.

## When one host stops fitting

Separate data services when measurements show meaningful contention, when independent maintenance windows or failure domains matter, when security boundaries require it, or when recovery goals exceed what one host can provide. Moving PostgreSQL to a managed service can reduce host maintenance but adds network, IAM, cost and provider dependencies. Moving Redis adds a network hop and operational contract; it may not be useful if a small local cache already meets measured needs. Keep application changes and data migration reversible where possible, and verify consistency before directing production traffic to a new authority.

## Failure scenarios and exercises

If the application reports connection refused, check the actual socket or address, listener and service state. If it reports authentication failure, inspect the application role, credential source and matching HBA rule without printing secrets. If connection counts spike, identify callers and their pool limits; increasing `max_connections` may intensify memory pressure. If requests slow while CPU remains low, inspect disk latency, locks, pool waits, swapping and dependency timing. If Redis restarts and orders disappear, the data model accidentally made the cache authoritative; restore the source of truth and fix that contract before retrying cache recovery.

1. Draw the memory budget for API, PostgreSQL, Redis, kernel and page cache under peak concurrency. Which measurements would cause a resize or separation?
2. Choose a PostgreSQL backup approach for a fictional Harbor recovery objective. State expected data loss, restore steps, storage location and the date of the last successful restore test.
3. The Redis cache is empty after reboot and database latency rises. What does the application do? How will you protect the database from a thundering herd while rebuilding derived values?
4. Determine whether the application uses TCP or Unix sockets for each service, then trace the least-privilege permissions that allow it.

**Answer guidance:** For exercise 1, add API, worker, PostgreSQL, cache, kernel/page-cache and backup/recovery headroom; sum simultaneous connection pools and query-memory consumers, then use measured peak pressure and latency to decide whether to reduce concurrency, resize or separate a service. For exercise 2, choose logical dump/restore for a portable periodic copy when its tested RPO/RTO suffice; choose base backup plus WAL archiving for point-in-time recovery, and state which recovery points are lost if archiving stops. For exercise 3, use jittered bounded retries, request coalescing and a concurrency limit around cache regeneration so a cold cache cannot stampede PostgreSQL. For exercise 4, TCP requires the intended listener and narrow HBA rule; a Unix socket requires the correct socket directory and OS/group permissions. In either case, do not broaden access until logs and the service identity show which boundary denied it.

On a small VPS, simplicity is useful only while resource ownership and recovery remain explicit. PostgreSQL owns accepted business records here; Redis is expendable because its contents can be rebuilt. As Harbor grows, measurements and recovery requirements decide whether that arrangement should change.

## Sources and verification

The official PostgreSQL 18 [connection](https://www.postgresql.org/docs/18/runtime-config-connection.html), [resource consumption](https://www.postgresql.org/docs/18/runtime-config-resource.html), [logical dump](https://www.postgresql.org/docs/18/app-pgdump.html), [restore](https://www.postgresql.org/docs/18/app-pgrestore.html), [backup methods](https://www.postgresql.org/docs/18/backup.html) and [monitoring roles](https://www.postgresql.org/docs/18/predefined-roles.html) documentation; Canonical's [Ubuntu PostgreSQL guide](https://documentation.ubuntu.com/server/how-to/databases/install-postgresql/); Red Hat's [RHEL 9 PostgreSQL](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_using_database_servers/using-postgresql_configuring-and-using-database-servers), [RHEL module installation](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/managing_software_with_the_dnf_tool/assembly_installing-rhel-9-content_managing-software-with-the-dnf-tool) and [Redis stream release notes](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/9.3_release_notes/new-features) documentation; Fedora's [Valkey package metadata](https://packages.fedoraproject.org/pkgs/valkey/valkey/fedora-42.html); and Redis [security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/) and [persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) documentation were inspected on 2026-10-04. These links identify named releases and examples, not a guarantee that every VPS image enables the same repository or service unit. The commands were syntax-checked but not run against a database host; distro service names and paths must be verified on the target image. No database, credential, firewall or cache was changed, and no restore rehearsal is claimed.
