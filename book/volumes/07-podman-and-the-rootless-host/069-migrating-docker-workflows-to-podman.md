---
book: The Complete DevOps Engineering Book
volume: 7
volume_title: "Podman and the Rootless Host"
chapter: 69
title: "Migrating Docker Workflows to Podman"
slug: migrating-docker-workflows-to-podman
status: complete
summary: ../../_ai/chapter-summaries/069-migrating-docker-workflows-to-podman.md
---

# Chapter 69 — Migrating Docker Workflows to Podman

## Compatible commands and behavioral differences

DispatchDesk's fictional VPS team already has Docker image builds, a Compose development environment and production runbooks. It wants rootless host services, but replacing `docker` with `podman` everywhere would conflate application portability with engine compatibility. A measured migration keeps the application's contract stable and verifies every operational boundary that changes.

Read [Buildah and Skopeo](068-buildah-and-skopeo-workflows.md), [Docker Compose](../06-docker-in-practice/057-docker-compose-for-multi-service-applications.md), and [Quadlet](066-quadlet-and-systemd-integration.md). This chapter uses a disposable local Linux host with one ordinary Podman account, registry access, `curl` and free TCP port 8092. A Compose provider must be installed separately through an approved source compatible with the selected distribution. The chapter does not assume an unavailable DispatchDesk image or an existing database.

Begin with an inventory rather than a rename. Record production image references/digests, build features, container users, storage sources, network aliases, exposed ports, secrets, logging, health checks, supervision and API-dependent tooling. Identify whether each component is portable image content, engine configuration, host policy or application data. These categories determine the migration method.

OCI-compatible images often run under both engines, while stores remain independent. Docker daemon images do not automatically appear in the ordinary user's Podman store. Pull the approved digest from the same registry or transfer it through an approved image transport. Confirm target architecture and runtime acceptance. Do not rebuild an already approved release merely to move it between engines unless the build process itself is part of the intended change.

Container data also does not migrate with the image. Docker volume names are not Podman volume names with shared content. Plan database-specific backup/restore, write cutover and ownership/label acceptance. A raw archive of a live database directory is not a safe migration procedure. Use [database operations](../04-vps-and-server-operations/036-database-and-cache-operations-on-one-host.md) and [backup/restore](../04-vps-and-server-operations/037-server-backups-and-restore.md) for those consistency requirements.

Command resemblance helps with individual `run`, `inspect`, `logs` and `exec` operations. It does not promise identical logging defaults, DNS behavior, network forwarding, resource enforcement, stop handling or restart after reboot. An alias also does not rewrite scripts that call a binary by an absolute path, interact with an API, or rely on Docker-specific output fields. Keep command names explicit during evaluation so failed assumptions remain visible.

Rootless execution changes authority and mapping. An image that wrote into a host bind mount as root under Docker may be denied under Podman. Diagnose that against the chosen user namespace and mandatory policy, not by adding `--privileged`. Resource limits deserve actual cgroup evidence. Boot durability deserves a user-manager test. A passing unit test suite cannot establish these host behaviors.

## Compose providers and socket compatibility

`podman compose` is a wrapper around an external Compose provider rather than a built-in reimplementation of the entire Compose specification. The provider's version, path and engine interaction therefore belong in the migration record. The [Podman compose manual](https://docs.podman.io/en/stable/markdown/podman-compose.1.html) describes provider selection and precedence. Check the installed provider instead of assuming a familiar command name identifies one implementation.

One integration path invokes a provider that knows how to drive Podman. Another uses a Docker-compatible API client against Podman's socket. Socket compatibility is an API boundary with supported behavior, not a guarantee that every Docker plugin, BuildKit feature or extension works. A tool that can list containers may still fail to create its required network or perform a build.

For the API path, enable the user socket under the owning ordinary account on the disposable host:

```bash
systemctl --user start podman.socket
systemctl --user status podman.socket
test -S "$XDG_RUNTIME_DIR/podman/podman.sock"
```

This starts socket activation for the account's API service. It is not required for ordinary local Podman commands. The socket path is associated with the execution account's runtime directory. Do not fabricate another user's runtime path or expose an unauthenticated TCP listener because a client expects Docker. The [API service manual](https://docs.podman.io/en/stable/markdown/podman-system-service.1.html) explains its compatibility and native APIs and the authority of access.

If a specific Docker Compose executable is the approved provider and needs explicit selection, first locate it with `command -v docker-compose` or the provider's installation record. Docker CLI plugin packaging may use another invocation/path, so select a real executable according to local Podman documentation. `PODMAN_COMPOSE_PROVIDER` can choose the provider; a nonexistent path should fail rather than silently becoming a different tool. Record the choice in CI and developer setup.

Do not place the engine socket inside the application container merely because a testing library requests it. That gives the application engine-control authority over the owning account's resources. Isolate test tooling and document its need. A rootless socket narrows authority compared with a rootful socket, but it still exposes that account's mounts, images and credentials.

## A bounded Compose acceptance fixture

Create a fresh working directory:

```bash
mkdir -m 700 "$HOME/dd-compose-69"
cd "$HOME/dd-compose-69"
```

Save this as `compose.yaml`:

```yaml
services:
  web:
    image: docker.io/library/nginx:alpine
    ports:
      - "127.0.0.1:8092:80"
    labels:
      org.dispatchdesk.lab: "chapter69"
```

This file isolates provider/API and host-publication acceptance from application and database concerns. It avoids `container_name` so project scoping can distinguish multiple environments. The image tag remains illustrative; digest pinning is required for a real release. A minimal fixture passing does not establish support for every feature in DispatchDesk's full development file.

Use the selected provider through Podman:

```bash
podman compose version
podman compose -p dd-migrate-69 config
podman compose -p dd-migrate-69 up -d
podman compose -p dd-migrate-69 ps
podman --remote=false ps --all
curl --fail --show-error --max-time 5 http://127.0.0.1:8092/
podman compose -p dd-migrate-69 logs --tail 50 web
```

These subcommands are interpreted by the selected external provider. Confirm them in its help/version before use. `-p` fixes a project name so cleanup does not depend on the directory's basename. `config` reveals the rendered deployment, including substituted environment values; treat its output as potentially sensitive. `up -d` creates local resources, and HTTP acceptance tests the service path independently of provider status.

For the full application, add one migration concern at a time: its approved image, runtime user, configuration, network dependency, persistent storage and health behavior. Compare observed outcomes with the previous engine. Compose ordering is not automatically application readiness; the [Docker startup-order reference](https://docs.docker.com/compose/how-tos/startup-order/) documents conditions for Docker Compose, and the selected Podman provider must be checked separately. Applications should survive dependency unavailability according to their own bounded retry contract.

Cleanup for this data-free fixture is:

```bash
podman compose -p dd-migrate-69 down
rm -- compose.yaml
cd "$HOME"
rmdir -- "$HOME/dd-compose-69"
```

Do not add volume-deletion flags to a data-bearing migration teardown. A test cleanup command and a production decommission procedure have different intent. Stop the Podman socket only if this lab started it and no other integration needs it; do not change a preexisting activation policy blindly.

## A measured migration checklist

Use a comparison table with actual evidence, not “compatible” checkmarks based on names:

| Boundary | Required evidence | Rollback concern |
|---|---|---|
| Image | Approved digest, target platform, application tests | Preserve old artifact and runtime configuration |
| Identity | Effective process UID and host mapping | Files written under new owners |
| Data | Consistent restore and representative transactions | Writes made after cutover |
| Network | Internal DNS, proxy upstream, source address and external probe | Old listener/route availability |
| Supervision | Stop, restart, logout and boot | Competing lifecycle owners |
| API tooling | Exact provider/client version and required calls | Restore known endpoint selection |
| Operations | Logs, metrics, resource limits and restore runbook | Evidence continuity across engines |

The cutover owner should define a reversible window and data strategy. For a stateless HTTP service, keep the old deployment stopped but reproducible and switch a tested proxy upstream. For a database writer, prevent two independently migrated instances from accepting writes against divergent stores. A traffic rollback may require replay or deliberate data reconciliation after new writes; it is not always reversible just by restoring the proxy address.

The fictional VPS team can choose Quadlet for production and retain Compose for developer environments. This is reasonable when systemd supervision matches its host operations model. Its fictional Kubernetes team may keep separate cluster manifests. Shared image and application contracts minimize divergence without requiring one lifecycle format everywhere.

## Failure, diagnosis and recovery

Suppose the provider says it cannot connect to `/var/run/docker.sock`. The failed assumption is that selecting Podman makes every external client automatically use its user socket. Verify which executable ran, its endpoint configuration, user socket state and execution account. A one-command endpoint override for a documented client can be useful; avoid exporting a global `DOCKER_HOST` in a shared shell and later forgetting it when using the real Docker engine.

Suppose `config` succeeds but `up` rejects a feature. Configuration parsing established syntax/rendering, not engine support. Reduce the failure to the specific unsupported resource or API request, compare installed provider documentation and choose a supported design. Preserve a known working fixture so an application-level problem is not mistaken for socket failure.

Suppose the old Docker workload works while Podman cannot write attachments. Inspect actual mount source, mapping, Unix permissions and SELinux/AppArmor. Do not copy Docker's graph root into Podman's store. The portable unit is an approved image artifact and consistently backed-up application data, not private engine metadata.

Before retiring Docker, run an operational game day: failed startup, unavailable registry, host reboot, restored data and rollback. Declare which tests remain unperformed. Migration is complete only when the new operational path meets the stated contract and the old data/service can be decommissioned deliberately.

## Exercises and review questions

1. A CLI alias passes `ps` but a test library fails. **Guidance:** the library may call an API directly; identify endpoint, supported API behavior and required privileges.
2. Why does a minimal Compose fixture not establish full Compose compatibility? **Guidance:** provider version and each feature/API call need separate evidence.
3. Design rollback after new attachment writes. **Guidance:** preserve data continuity, prevent split writers and determine whether the old image accepts new data format/owners.
4. Choose developer and production lifecycle formats for a single-host team. **Guidance:** optimize for team operations and application parity, not a mandatory one-tool policy.

## Takeaways and further reading

Migrate runtime contracts and operational evidence, not command spelling. Keep provider, endpoint and data ownership explicit. Continue with [host operations and incidents](070-podman-host-operations-and-incidents.md).

Podman compose/API service and Docker Compose startup-order documentation were inspected 2026-10-03. No provider installation, socket activation, Compose deployment or Docker-to-Podman data migration was performed by the author.
