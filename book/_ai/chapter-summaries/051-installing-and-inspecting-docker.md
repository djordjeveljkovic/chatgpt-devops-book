# Chapter 51 — Installing and Inspecting Docker

Status: complete

## Written material
Ubuntu APT and distinct Fedora/RHEL DNF installation; release and conflict cautions; rootful privilege; initial disposable smoke test and named retry preserving exit/log evidence; explicit sudo local-socket verification; unprivileged target/environment/config inspection; bounded installation exercise, expected evidence, answer guidance, takeaways and relative navigation.

## Concepts and terminology
Docker Engine client/server, package source/signing key, rootful daemon authority, context endpoint, `DOCKER_HOST`, `DOCKER_CONTEXT`, `DOCKER_CONFIG`, global `--host`/`--context`, stop/exit evidence.

## Examples and cross-references
Official repository install commands; `sudo --host unix:///var/run/docker.sock` version/info; ordinary user's context/override diagnostics; `hello-world` with `--rm` and named retained variant. Links to chapters 46, 47, 50 and 52. No host commands executed.

## Open threads
Distribution support matrix is time-sensitive; exact installed package availability requires target-host confirmation. No package installation or Docker daemon verification was run.

## Exact next section
None. Independently approved; continue with Chapter 52.

## Verification
Official Docker Ubuntu/Fedora/RHEL, post-install, context, run, remove and firewall docs inspected 2026-10-02; context precedence additionally checked 2026-10-03. Independent review passed with seven shell checks and 1,271 local links. Current Chapter 51–52 checker passed with 12 shell checks and 1,274 links. No installation or daemon verification was run.
