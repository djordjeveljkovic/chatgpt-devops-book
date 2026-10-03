---
book: The Complete DevOps Engineering Book
volume: 7
volume_title: "Podman and the Rootless Host"
chapter: 63
title: "Rootless Identity and Volume Ownership"
slug: rootless-identity-and-volume-ownership
status: complete
summary: ../../_ai/chapter-summaries/063-rootless-identity-and-volume-ownership.md
---

# Chapter 63 — Rootless Identity and Volume Ownership

## Subordinate IDs and mappings

DispatchDesk's rootless service needs to write attachments to a dedicated directory. The host account owns that directory, but an image update changes the application's container UID to 1000. The service now fails with permission denied. The useful question is which host identity that container UID becomes. Matching the number printed inside the container to a username on the host does not answer it.

Read [rootless fundamentals](../05-container-internals-and-oci/047-rootless-containers-and-user-mapping.md) and [ordinary permissions](../02-linux-and-automation/014-users-groups-and-permissions.md) first. The following labs run locally on a disposable Linux Podman host as its ordinary owning account. They use a dedicated directory under that account's home, not a database path. BusyBox provides `id`, `stat` and a shell; registry access is required. No real DispatchDesk data is involved.

Inspect configuration before changing anything:

```bash
id
getent passwd "$(id -un)"
awk -F: -v account="$(id -un)" '$1 == account { print }' /etc/subuid
awk -F: -v account="$(id -un)" '$1 == account { print }' /etc/subgid
podman --remote=false unshare cat /proc/self/uid_map
podman --remote=false unshare cat /proc/self/gid_map
```

The subordinate files commonly record account, starting ID and count. Some environments use another configured subordinate-ID provider, so empty file output needs investigation rather than an immediate manual append. The maps describe inside start, outside start and range length. Each range translates IDs arithmetically. Read UID and GID maps independently; identical-looking ranges are a policy choice, not a kernel requirement.

For illustration only, a default rootless map might contain container ID 0 mapped to host UID 1001 for one ID, followed by container ID 1 mapped to host UID 200000 for 65536 IDs. Container UID 1000 then maps to host UID 200999. This is not your machine's measured allocation. A different namespace mode can produce a different mapping. Host files created by that identity will show the mapped number when no host username exists for it.

`podman unshare` enters Podman's rootless user namespace for local maintenance and diagnostic commands. Its map is especially useful for the default rootless namespace; do not assume it describes a container using `keep-id`, `auto` or explicit mappings. The [unshare manual](https://docs.podman.io/en/stable/markdown/podman-unshare.1.html) documents this local feature. To reason about a particular container, inspect its effective namespace configuration and, where authorized, actual process maps.

Administrators manage subordinate ranges across the host or fleet. Overlapping allocations undermine isolation and make ownership ambiguous. Changing them while containers are active can leave files owned by old numbers. An account's namespace keeper can also retain previous mappings. Coordinate an outage, stop dependent workloads, preserve consistent backups and follow [system migrate](https://docs.podman.io/en/stable/markdown/podman-system-migrate.1.html) guidance when changing mappings. That operation can stop running containers; it is not a harmless refresh command.

Ubuntu's `uidmap` package supplies mapping helpers. Fedora/RHEL package dependencies and account provisioning may supply the needed tools and allocations differently. Inspect installed packages and host policy instead of assuming an Ubuntu package command applies everywhere. On any distribution, NFS home directories and rootless graph storage require special care because remote filesystems may not implement the expected ownership semantics.

## Keep-id, unshare and file ownership

First demonstrate a deliberate identity choice. Create a disposable directory; stop if it already contains data from another exercise:

```bash
lab_dir="$HOME/dd-ownership-63"
mkdir -m 700 "$lab_dir"
podman --remote=false run --rm --userns=keep-id \
  --volume "$lab_dir:/data:Z" \
  docker.io/library/busybox:1.37 \
  sh -c 'id; printf "attachment fixture\n" > /data/marker; stat -c "%u:%g %a %n" /data/marker'
stat -c '%u:%g %a %n' "$lab_dir/marker"
```

`keep-id` maps the invoking account into the container with the same numeric UID/GID and normally selects that user for the container's initial process unless overridden. Consequently, this fixture writes as the account that owns the directory. The [run manual's user namespace section](https://docs.podman.io/en/stable/markdown/podman-run.1.html#userns-mode) documents the options; check the installed release before combining namespace modes.

`:Z` labels this dedicated bind source for a private container on enforcing SELinux hosts. It is not an ownership repair. Ubuntu commonly uses AppArmor instead; it does not acquire SELinux policy merely because a volume suffix is present. Chapter 67 treats that layer separately. Do not relabel an entire home directory or a system directory to extend this fixture.

Now reproduce a Unix ownership mismatch intentionally. Keep the same host-owned directory and create a retained failing fixture with an explicit different container UID:

```bash
podman --remote=false run --name dd-denied-63 --user 1000:1000 \
  --volume "$lab_dir:/data:Z" \
  docker.io/library/busybox:1.37 \
  sh -c 'id; printf "unexpected write\n" > /data/denied'
podman --remote=false inspect dd-denied-63
podman --remote=false logs dd-denied-63
```

The intended failure is a denied write when the default map translates UID 1000 to a host identity without directory access. It may not fail if your effective mappings or ACLs differ; inspect them rather than claiming the experiment proved a universal rule. The ordinary host account owns a mode-700 directory. That account's membership in a familiar group does not grant a subordinate identity the same group access automatically.

Choose a repair according to the image's runtime contract. If the application supports running as the caller's UID, `keep-id` may be sufficient. If the image requires a fixed internal UID, current Podman provides `keep-id:uid=1000,gid=1000` to map the invoking account to those container IDs. Test the image's entrypoint, writable paths and group expectations before adopting it. An application that requires root-only startup cannot be made compatible merely by changing its final worker UID.

## Repairing persistent-volume access

For this fixture, map the account to the application's desired IDs and retry as a new object:

```bash
podman --remote=false run --rm \
  --userns=keep-id:uid=1000,gid=1000 --user 1000:1000 \
  --volume "$lab_dir:/data:Z" \
  docker.io/library/busybox:1.37 \
  sh -c 'id; printf "repaired write\n" > /data/repaired'
stat -c '%u:%g %a %n' "$lab_dir/repaired"
podman --remote=false rm dd-denied-63
```

The change repairs the credential relationship without recursively changing the host directory's ownership. Verify inside IDs, outside ownership and successful access. In production, verify existing files too: a new marker does not prove the service can read historic attachments or atomically rename files into a subdirectory.

Another valid design gives a dedicated volume to the application's mapped UID. For default mappings, `podman unshare chown` can express ownership in namespace IDs. This changes real host ownership. Only perform it after inspecting the map, stopping writers, backing up consistent data and confirming the source is wholly dedicated to that workload. A command aimed at the wrong path can recursively disrupt another service. Prefer a narrowly targeted file or newly created empty directory when learning; do not use a blanket recursive chown as the default incident response.

Podman's `:U` option also recursively adjusts source ownership to match the container user. It can traverse many files, delay startup, and leave host-visible ownership changed. It is not a reversible view of the mount. Record original ownership if that strategy is approved, and include startup time and restore identity in acceptance tests. Likewise, do not assume an idmapped mount is available rootlessly: upstream run documentation inspected for this chapter describes Podman's mount `idmap` option as rootful-only. Kernel and engine support must be checked for the selected design.

Named volumes reduce accidental host-path selection but do not remove UID/GID or backup requirements. Inspect the actual volume and mountpoint using [volume inspect](https://docs.podman.io/en/stable/markdown/podman-volume-inspect.1.html). A replacement application may need a data-format migration in addition to an ownership adjustment. Separate those changes so a failed format conversion is not misdiagnosed as a mode-bit problem.

## Diagnose before broadening access

For a denied write, walk through source existence, parent-directory search permissions, mapped UID/GID, ACLs, read-only mount state and mandatory security policy. A `chmod 777` experiment changes the data exposure and may still fail under SELinux. A rootful rerun changes the authority and store, and may create root-owned files that break later rootless launches. Neither is an acceptable explanation of the original failure.

Suppose restored files belong to yesterday's subordinate range. Preserve the backup and record both old and new mappings. Decide whether to restore the account allocation or translate dedicated data into the new allocation. Verify a representative set of files and application operations before reopening writes. A restore that preserves numeric owners faithfully can still be operationally wrong on a host with different mapping policy.

Cleanup removes only the lab files and empty dedicated directory:

```bash
rm -- "$lab_dir/marker" "$lab_dir/repaired"
rmdir -- "$lab_dir"
```

If unexpected files prevent `rmdir`, inspect them. Do not convert the cleanup into recursive deletion without confirming their provenance.

## Exercises and review questions

1. Calculate the host UID for container UID 42 under the illustrative map above. **Guidance:** 200041; subtract the inside range start before adding the outside start.
2. Why does `:Z` not repair a numeric ownership mismatch? **Guidance:** mandatory labels and discretionary ownership are independent checks.
3. Compare `keep-id` with `:U`. **Guidance:** the first changes mapping/process identity; the second changes actual source ownership and can traverse existing data.
4. Design acceptance for restoring attachment files to another host. **Guidance:** validate allocation policy, UID/GID translation, labels, representative reads/writes/renames and consistent application state.

## Takeaways and further reading

Ownership repair begins with the effective mapping and application UID contract. Preserve account allocations as part of recovery design. Continue with [networking](064-podman-networking-and-ports.md).

Primary Podman unshare, system-migrate and volume-inspect documentation, plus the run identity/mount sections, were inspected 2026-10-03. No ownership mutation, volume operation or container lab was executed by the author.
