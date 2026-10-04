---
book: The Complete DevOps Engineering Book
volume: 18
volume_title: "Security and Software Supply Chains"
chapter: 173
title: "Container Security in Practice"
slug: container-security-in-practice
status: complete
summary: ../../_ai/chapter-summaries/173-container-security-in-practice.md
---

# Chapter 173 — Container Security in Practice

**Section outline:** control image inputs and runtime privilege; use rootless execution and workload isolation with explicit limits; review a real container posture through inspectable evidence and recovery.

## Image content and runtime privilege

A container packages a filesystem and process configuration; it still shares the host kernel. Namespaces, cgroups, capabilities, seccomp, and mandatory access control reduce what a process can see or do, but they do not make an untrusted workload equivalent to a separate machine. A container escape can expose the host, and a container with a writable host bind mount or a privileged API socket can already hold broad host authority without any kernel exploit. Start with the threat model from [Chapter 171](171-threat-modeling-for-operators.md) and the host controls in [Chapter 172](172-host-security-and-patch-management.md): identify the data, credentials, kernel, runtime and adjacent services at risk, then inspect both the image and how it is launched.

Image risk begins with its inputs. The `FROM` line selects software and an upstream publisher; package installs and downloaded archives add more publishers and update paths. Pinning a base image by digest identifies fixed content, but does not show who built it or whether it is appropriate to trust. A tag such as `stable` can move. Use an approved base image, record its digest, update that digest through reviewed changes, and rebuild regularly so security fixes arrive. A digest can make an old vulnerable image reproducible, so immutability needs an update process. [Chapter 178](178-artifact-signing-and-provenance.md) covers signing and provenance in detail.

Build only the runtime artifacts needed by the service. Multi-stage builds can keep compilers, package managers and source trees out of a production stage. A smaller filesystem reduces unnecessary components; it does not guarantee fewer exploitable bugs or eliminate runtime dependencies. Keep OS packages current, pin application dependencies using the ecosystem's lock mechanism, and scan the resulting image against the selected vulnerability database. Treat a scan as a time-stamped result for a specific image digest and database state. It can miss vulnerabilities, report false positives, or overlook code that is not in its database. A green scan is one signal, not a release approval.

Never bake production credentials into an image. Files copied during an early build layer may remain recoverable from the image even after a later deletion. Docker warns that build arguments and environment variables are inappropriate secret channels because they can persist in image metadata or history; use the builder's secret mount mechanism for temporary build access. At runtime, supply credentials through a managed secret channel with the smallest audience and lifetime possible. Avoid printing them during builds, test reports, process arguments or startup logs. A private registry controls access to stored images but does not prove that every image in it is safe.

An unprivileged application user is a strong default. Set `USER` in the final image, make writable directories explicit, and avoid adding `sudo` or a shell merely for operator convenience. Confirm the program works with its assigned UID, filesystem permissions and signal-handling behavior. If the application needs to bind a low port, prefer an unprivileged listener behind a host or proxy mapping over granting extra capabilities without a reason. Do not treat root inside a container as harmless: in a rootful runtime, namespace configuration and retained capabilities determine how that identity relates to host authority.

Inspect the effective runtime settings as well as the Dockerfile. Important questions include: which user runs the process; which capabilities remain; whether privilege escalation is possible; what is mounted writable; which devices are exposed; which host namespaces are shared; which network peers can be reached; and whether seccomp and SELinux/AppArmor confinement are active. Avoid `--privileged`, host PID/network namespaces, broad host mounts, and mounting the container-engine socket unless the threat model specifically justifies the resulting authority. A container with `/var/run/docker.sock` can often ask a rootful daemon to create a host-privileged container. Calling the workload “isolated” does not change that API's authority.

## Rootless operation and workload isolation

Rootless Docker or Podman starts the engine under a non-root user. User namespaces map container identities onto host identities; in Podman's rootless mode, UID/GID mappings use subordinate ID ranges configured for the account, and containers belong to the invoking user rather than root-managed storage. This reduces the host authority available through a runtime or kernel flaw, but is not a complete sandbox. A process can still damage files the account can access, consume that user's permitted resources, reach services allowed by network policy, or expose data through unsafe mounts. Rootless support also depends on kernel features, subordinate IDs, storage drivers, networking setup and user-session/service design. Validate those prerequisites and the filesystem ownership model on the target host.

Rootless and non-root-in-container solve related but distinct problems. The image's `USER` controls the process identity in the container; rootless mode controls which host identity and namespace mapping backs the engine. A rootless container whose process appears as UID 0 may map that identity to the unprivileged invoking user on the host. Conversely, a rootful engine can run a process as UID 10001 while retaining powerful host-facing mounts or runtime settings. Use both where practical, then inspect the mapping and mounts rather than inferring host risk from the displayed container UID.

Constrain each workload by least privilege. Drop unused Linux capabilities, deny privilege escalation, keep the root filesystem read-only where the application permits it, and mount only specific writable data paths. Use a temporary filesystem for scratch data and set resource controls so one process cannot starve neighbors. Preserve default seccomp and mandatory-access-control profiles unless an observed, documented requirement demands a narrow adjustment. These controls are defense in depth: if the application is compromised, an attacker should still have limited filesystem writes, kernel interfaces, credentials and network destinations.

Example: run a reviewed DispatchDesk worker as a rootless Podman container. This is a command template for an operator account with Podman configured rootlessly and an existing named network and persistent data volume. Replace the image placeholder with the exact approved registry digest and confirm the image's expected UID and writable paths before use; the text is not a tested launch result.

```bash
IMAGE_REF='registry.example/dispatchdesk-worker@sha256:<approved-digest>'

podman run --detach \
  --name dispatchdesk-worker \
  --user 10001:10001 \
  --cap-drop=all \
  --security-opt=no-new-privileges \
  --read-only \
  --read-only-tmpfs=false \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --mount type=volume,source=dispatchdesk-work,target=/var/lib/dispatchdesk \
  --network dispatchdesk-backend \
  "$IMAGE_REF"
```

The operator runs this without `sudo`; `--detach` leaves the process managed in the background, `--name` makes it addressable by a stable local name, `--user` selects the process identity, `--cap-drop=all` removes Linux capabilities, and `--security-opt=no-new-privileges` prevents gaining additional privilege through set-user-ID or file capabilities. `--read-only` makes the container's root filesystem read-only. Podman's default `--read-only-tmpfs=true` adds writable temporary mounts at `/dev`, `/dev/shm`, `/run`, `/tmp` and `/var/tmp`; the explicit `--read-only-tmpfs=false` disables those tmpfs mounts and marks `/dev` and `/dev/shm` read-only. This example then adds only a bounded writable `/tmp` scratch mount. Applications that need runtime files in `/run`, temporary files in `/var/tmp`, shared memory in `/dev/shm`, or device writes must be tested and given only the necessary explicit mount or device access. The named volume is the persistent write location. `--network` connects it to the pre-created network. The command changes local container state and may start application traffic. It does not configure a health check, resource limit, restart policy or remote exposure; those must match the actual service contract and process manager.

If startup fails, do not remove protections in bulk until the cause is known. Check the process exit, logs, configured user, volume ownership, required writable paths, network name and SELinux/AppArmor denials. A volume created by another UID mapping can appear unwritable; fix the ownership/mapping deliberately rather than running as root or relabeling arbitrary host paths. If the application genuinely requires one capability or writable directory, document the exact need and grant only that capability or path. Preserve effective denial evidence as part of the review.

## Reviewing a container security posture

DispatchDesk's worker image passes its scanner with no critical findings, and a reviewer assumes it is safe to deploy. An incident reveals that the worker container mounts `/var/run/docker.sock` and starts as root. The CI job copied the socket into the deployment definition from a local debugging example. A compromised worker could use the host's rootful Docker daemon to create a privileged container and alter the host. The scanner assessed packages in image content; it did not assess the effective runtime authority. The failed assumption was that image contents alone describe container security.

Review the image and the instantiated workload separately. Identify the immutable image reference, publisher, build source and scan timestamp. Then inspect the actual container configuration from the runtime: image ID, process user, mounts and modes, capabilities, security options, namespace settings, devices, network attachment and restart behavior. Compare observed state with a reviewed deployment file and the host's runtime policy. A Compose file or Podman unit is desired configuration; the engine's inspection output shows the created object. Both can be stale or incomplete, so also verify host-level policy, effective network reachability and service identity.

For Docker, inspect with `docker inspect <container>` and use `docker image inspect <image>` for image metadata. For Podman, use `podman inspect <container>` and `podman image inspect <image>`. These are read-only inspection commands, but output can include environment values and labels; restrict the terminal transcript and redact secrets before attaching evidence to a ticket. `docker history --no-trunc <image>` can help locate image-layer metadata, but it cannot establish absence of every leaked secret. A secret rotated after being embedded is still a leaked credential and must be treated as such.

In the incident, stop further deployments and isolate the affected worker's network path while preserving host daemon, runtime and CI audit logs. Do not immediately delete the container or prune images: those actions can destroy evidence. Remove the socket mount and root privilege in a reviewed deployment change, rotate any credentials the workload could access, rebuild from a reviewed source and approved base digest, and redeploy a restricted instance. Inspect the host for unexpected containers, files, users and daemon API activity. Restore service only after the worker's queue behavior, duplicate handling and provider permissions have been checked. If the host may have been controlled through the daemon, rebuild it from a trusted image and reconcile application data before declaring recovery; recreating one container does not restore host trust.

When replacing an unaffected container during routine rollout, drain or stop it according to the service's delivery contract, then remove only the container object after the replacement is healthy. For this example, `podman stop dispatchdesk-worker` followed by `podman rm dispatchdesk-worker` removes the stopped container and preserves the separately managed `dispatchdesk-work` volume. Do not add `--volumes` or prune volumes as casual cleanup; confirm backups and data ownership before removing persistent storage. During an incident, preserve the original container and image evidence until responders have captured what they need.

Make the review reproducible. Record the date, image digest, runtime version, host kernel, effective command/configuration, scanner and database version, exception approvals, findings, evidence paths, responsible owner and retest deadline. A saved `inspect` output is a snapshot, not a continuous guarantee. Repeat review when the image digest, runtime, kernel, mount, identity or network policy changes. Where possible, make policy checks block known-dangerous settings such as privileged mode, host socket mounts, root execution without an exception, or unapproved registries. Keep those rules tied to observed environment needs so teams have a supported path to request and test a narrow exception.

Exercises:

1. A container runs as UID 10001 but mounts the engine socket read/write. Which identity is the strongest host authority in this example, and what should be removed first?
2. A rootless Podman service cannot write to its named volume after migration to another host. What mapping and ownership evidence should be checked before changing the workload's user?
3. A scanner reports zero critical findings for an image, but its runtime has `--privileged` and host networking. Explain what the scanner did and did not establish, and propose a review gate.

Answer guidance: the rootful engine socket may allow callers to request host-level operations, so remove that mount and investigate possible daemon use; the container UID does not neutralize the socket's authority. For rootless storage, inspect `/etc/subuid`, `/etc/subgid`, user namespace mappings, volume ownership and mount options on source and target hosts; do not blindly chown host data. A package scanner describes known image findings for a particular database/time. It does not evaluate runtime privileges, host exposure, build provenance or application behavior. Add effective runtime inspection/policy checks and investigate the deployment that enabled those settings.

Review questions:

- Why does a digest pin improve identity while saying nothing about who built the image?
- What risk does rootless execution reduce, and what user-level authority remains?
- Which evidence comes from image inspection, which from container inspection, and which must be verified on the host?

Takeaways:

- Treat container security as a combination of image inputs, runtime privileges, host kernel, mounts, identity and reachable services.
- Keep secrets out of image layers and build metadata; scan results are time-bound evidence, not a guarantee.
- Combine an unprivileged image user with rootless execution and narrow runtime access where supported.
- Compare desired deployment configuration with effective container and host state, then preserve evidence during response.

## Sources checked 2026-10-04

- [Docker Engine security](https://docs.docker.com/engine/security/) — daemon authority, capabilities and runtime isolation limits.
- [Docker rootless mode](https://docs.docker.com/engine/security/rootless/) — rootless prerequisites and user-namespace model.
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/) — image inputs, rebuilding and digest pinning tradeoffs.
- [Docker build secrets](https://docs.docker.com/build/building/secrets/) — secret mounts and why build args/environment variables are unsuitable for secrets.
- [Docker seccomp profiles](https://docs.docker.com/engine/security/seccomp/) — default profile behavior and override risks.
- [Podman 6.1.3 manual](https://docs.podman.io/en/v6.1.3/markdown/podman.1.html) — rootless user namespaces and subordinate UID/GID setup.
- [Podman run manual](https://docs.podman.io/en/latest/markdown/podman-run.1.html) — read-only root filesystems and runtime security options.

These references and version assumptions were checked on the listed date. No image build, scan, container launch, host inspection, exploit, rootless migration, runtime policy or incident response was executed.
