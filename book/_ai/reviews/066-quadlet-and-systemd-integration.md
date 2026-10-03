# Independent review — Chapter 66

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 50c458357835ea8ffd85fce96cef474e76548239f2f5f071a648033234bd4682

## Findings, inspection and dated evidence

No unresolved material finding. Reviewed source/generated-unit distinction, user search paths, cgroup v2 prerequisite, install-section boot activation, linger as a persistent host change, user versus system manager ordering, one restart owner, start/stop limits, image-pull/startup timing, application readiness and source/digest rollback. The exact source uses documented Container keys and standard systemd sections. Exercises provide answer guidance and a closing takeaway. Ubuntu 24.04, Fedora and RHEL feature/version differences are explicitly bounded by installed-manual checks rather than claiming uniform upstream support.

Primary evidence: [Quadlet systemd manual](https://docs.podman.io/en/stable/markdown/podman-systemd.unit.5.html), [container-unit manual](https://docs.podman.io/en/stable/markdown/podman-container.unit.5.html), and official [loginctl source manual](https://raw.githubusercontent.com/systemd/systemd/main/man/loginctl.xml), inspected during this review on 2026-10-03/04. The packaged generator reports 6.1.2. Extracted the exact .container source to a temporary directory and ran `/usr/lib/podman/quadlet --user --dryrun` with `QUADLET_UNIT_DIRS` pointing only there: exit 0 and generated dd-http-66.service with notify supervision, expected container/name/publication/journald, 10-second stop flag, restart/start/stop policy, cleanup and WantedBy default.target. This generated text without installing or activating a user service. Temporary artifacts removed.

## Scope and validation limits

Read the authoring guide, assigned SKELETON brief and manuscript/summary, and prerequisite/rootless account summaries 61–65; checked the complete five-chapter sequence together and relevant canonical links. Summaries accurately distinguish static checks from unperformed runtime acceptance. `python tools/check_book.py --chapters 66-70` passed five drafts, 30 shell syntax checks, one YAML parse and 1,333 global local-link checks, with no errors or warnings. The embedded Python was separately compiled in this review. Static checking cannot establish runtime semantics or external-link uptime. Successfully retrieved primary sources are listed above; no exhaustive external-link availability audit is claimed.

Podman is installed but ordinary `podman --version` failed before reporting a version because the default runtime state path is read-only in this sandbox. The independent Quadlet binary reports 6.1.2 and can generate text in an isolated dry-run. Buildah and Skopeo are unavailable. No installed account configuration, systemd service, linger setting, container store, image, registry credential, host policy, network listener, engine socket, image build/copy, service boot or restore test was changed/executed. No runtime Ubuntu/Fedora/RHEL matrix was tested. Reviewer edited only separate review records; no manuscripts, summaries or shared metadata were changed.

Verdict: approved
