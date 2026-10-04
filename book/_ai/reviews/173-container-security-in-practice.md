# Independent review — Chapter 173

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 57a5c84bc4122e8302bd761f926094ef1ae376932201209378e8dbc425441ab6

## Scope and findings

Read current full body/summary, assigned brief and authoring guide, with Chapters 171/172 security context. Inspected Podman launch syntax/assumptions, Docker/Podman metadata inspection, image identity/build-secret/scanner distinctions, rootless namespaces, runtime mount/network/capability boundaries, incident recovery and assessment. One command-behavior clarification required before approval.

Medium — Rootless operation and workload isolation, Podman template and immediately following flag explanation: the command enables --read-only without disabling Podman's default --read-only-tmpfs=true. Besides the explicit /tmp mount and persistent data volume, Podman supplies writable tmpfs mounts including /run and /var/tmp (and runtime /dev and /dev/shm). The explanation identifies the explicit tmpfs/volume as the write locations without explaining these additional writable paths. A security-posture example must state the effective boundary. Either retain defaults and explicitly list/explain these additional runtime writable mounts, or add --read-only-tmpfs=false and explain/test required runtime paths, noting the /dev and /dev/shm consequences. Do not claim that --read-only alone leaves only the manually declared scratch/data paths writable.

Low optional observations:

- Image content paragraph: Chapter 178 is a plain reference, while the summary calls it linked; use its actual relative link.
- Podman template: add controlled teardown/recovery instructions (stop/remove the named container while preserving the persistent volume), suitable for its explicitly state-changing launch. No cleanup command is currently supplied.
- Front matter is drafting and summary is draft; align during coordinator maintenance.

Other technical assessment: rootless host identity versus container USER is accurately distinguished, subordinate-ID prerequisites/mount ownership are acknowledged, and rootful engine socket authority is not neutralized by a non-root application UID. Launch flags, existing-network/volume assumptions and placeholder digest are otherwise coherent. Cap-drop/no-new-privileges, read-only root mount and scratch mount options have valid syntax. The text explicitly disclaims resource/health/restart-policy configuration. Named network attachment is not falsely promised to restrict all egress. Secrets via build arguments/image layers, digest versus provenance, scanner database/time limits and runtime-versus-image evidence are distinguished. Inspect/history output may expose secrets and is appropriately restricted. Recovery preserves evidence and treats possible daemon compromise as a host-trust issue, requiring trusted rebuild and data reconciliation rather than only recreating the workload. Exercises/questions/takeaways are substantive.

## Primary evidence checked 2026-10-04

- [Podman run manual](https://docs.podman.io/en/latest/markdown/podman-run.1.html): run syntax, user/capability/security/mount/network flags; read-only-tmpfs defaults and runtime writable mount boundaries.
- [Podman 6.1.3 manual](https://docs.podman.io/en/v6.1.3/markdown/podman.1.html): rootless account/subordinate IDs and namespace scope. Pinned reference is available; no latest-release assertion made.
- [Docker rootless mode](https://docs.docker.com/engine/security/rootless/): user namespaces/prerequisites and host non-root boundary.
- [Docker build secrets](https://docs.docker.com/build/building/secrets/): build argument/environment persistence risk and temporary secret mounts.

## Validation and limits

`python3 tools/check_book.py --chapters 173-173` passed one shell syntax check and 1,470 global local links without warnings/errors (state drafting). Exact body hash computed using `tools.promote_reviewed.body_hash`. Commands/control boundaries inspected statically against primary docs. No build/scan/container launch, image/container inspection, network access test, mount/user mapping migration, exploit or incident-response operation executed. No OS/kernel/runtime/storage-driver/security-policy matrix tested. Documentation cannot prove this placeholder image works as UID 10001, volume ownership is correct, actual scratch paths meet the service contract or host trust is restored. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

The Chapter 178 link, routine stop/remove guidance preserving named storage and incident evidence, and draft metadata alignment are resolved. The read-only explanation now describes --read-only-tmpfs=false, but the actual fenced podman run command still omits that flag. Therefore the original material effective-write-boundary finding remains unresolved: the command still enables default additional writable tmpfs mounts while its prose says those defaults are disabled. Add `--read-only-tmpfs=false` to the actual command. Also mention /var/tmp and /dev,/dev/shm in the default/consequence explanation, consistent with the current primary manual; disabling the option affects those paths too. Do not infer this correction from a prose-only reference.

Fresh body hash: 73bdb64be3e451b7424dc4afa8b249cb6047a7309ced7cda9f14da4c36c65ba5. `python3 tools/check_book.py --chapters 173-173` passed one shell syntax check and 1,471 local links without warnings/errors. Static checker does not detect this prose/flag mismatch. Earlier evidence and runtime limits remain applicable; only this review record updated.

## Final bounded correction refresh — 2026-10-04

Inspected the actual fenced launch and following explanation. The command now includes --read-only-tmpfs=false; prose accurately describes default writable /dev,/dev/shm,/run,/tmp,/var/tmp, disabling automatic scratch mounts and read-only /dev,/dev/shm consequences. The explicit bounded /tmp and persistent volume remain deliberate writable mounts, and application requirements for other runtime paths/device access require explicit testing and narrow grants. This resolves the material command/prose boundary finding against the previously checked Podman manual. Earlier optional corrections remain resolved; no material issue remains.

Fresh body hash from `tools.promote_reviewed.body_hash`: 57a5c84bc4122e8302bd761f926094ef1ae376932201209378e8dbc425441ab6. `python3 tools/check_book.py --chapters 173-173` passed one shell syntax check and 1,473 global local links without warnings/errors. Earlier full technical assessment, dated primary evidence and runtime/nonexecution limits remain applicable. No actual container or writable-path test claimed. Only this review record updated.

Verdict: approved
