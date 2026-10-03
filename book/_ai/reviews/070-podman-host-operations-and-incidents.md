# Independent review — Chapter 70

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: df661acc62946c5a565b8d1168c4a4953cbba96a0aba7de38f594a82f0067f04

## Findings, inspection and dated evidence

No unresolved material finding. Reviewed account-aware host inventory, graph-root/backing mount evidence, reclaim estimates versus physical usage, narrow deletion and retention, package/engine migration risks, canary/boot/restore tests, registry failure stages, persistent auth versus runtime credential file, correct host service environment placement, resource/account/host boundaries, OOM ambiguity, fleet identity and acceptance. Ubuntu versus Fedora/RHEL vendor lifecycle differences are explicit, and cross-volume package/backup/capacity topics use canonical links. Exercises have guidance and recovery returns to user-visible and durable-data acceptance.

Primary evidence: Podman [system df](https://docs.podman.io/en/stable/markdown/podman-system-df.1.html), [prune](https://docs.podman.io/en/stable/markdown/podman-system-prune.1.html), [migrate](https://docs.podman.io/en/stable/markdown/podman-system-migrate.1.html), [events](https://docs.podman.io/en/stable/markdown/podman-events.1.html), [login](https://docs.podman.io/en/stable/markdown/podman-login.1.html), [stats](https://docs.podman.io/en/stable/markdown/podman-stats.1.html) and [auto-update](https://docs.podman.io/en/stable/markdown/podman-auto-update.1.html), inspected on 2026-10-03/04. Login documentation confirms REGISTRY_AUTH_FILE. Added the exact proposed host [Service] Environment line to an isolated temporary copy of Chapter 66's source and ran generator 6.1.2 dry-run: exit 0, Environment=REGISTRY_AUTH_FILE=%h/.config/containers/registry-auth.json preserved in generated [Service]. No credentials created, specifier-expanded user service activated, registry contacted or container started.

## Scope and validation limits

Read the authoring guide, assigned SKELETON brief and manuscript/summary, and prerequisite/rootless account summaries 61–65; checked the complete five-chapter sequence together and relevant canonical links. Summaries accurately distinguish static checks from unperformed runtime acceptance. `python tools/check_book.py --chapters 66-70` passed five drafts, 30 shell syntax checks, one YAML parse and 1,333 global local-link checks, with no errors or warnings. The embedded Python was separately compiled in this review. Static checking cannot establish runtime semantics or external-link uptime. Successfully retrieved primary sources are listed above; no exhaustive external-link availability audit is claimed.

Podman is installed but ordinary `podman --version` failed before reporting a version because the default runtime state path is read-only in this sandbox. The independent Quadlet binary reports 6.1.2 and can generate text in an isolated dry-run. Buildah and Skopeo are unavailable. No installed account configuration, systemd service, linger setting, container store, image, registry credential, host policy, network listener, engine socket, image build/copy, service boot or restore test was changed/executed. No runtime Ubuntu/Fedora/RHEL matrix was tested. Reviewer edited only separate review records; no manuscripts, summaries or shared metadata were changed.

Verdict: approved
