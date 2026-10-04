# Independent review — Chapter 132

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 29da7c23bdacfa1bb03db4c4de13631a75de4993a80765a1c6e30ccc8e72d993

## Scope and findings

Read current entire chapter, summary, brief and authoring guide, with reviewed Chapter131 release identity context. Checked archive preconditions, GNU options, account/service boundaries, symlink replacement, health and recovery, platform distinctions and exercises. Hash computed using tools.promote_reviewed.body_hash matches supplied value.

**Medium — Define a systemd service contract, initial paragraph; exercise3 and answer3:** distinguish systemd reading EnvironmentFile from the application opening that file. The example recommends a root-readable environment file but says the unprivileged binary reads it; those are incompatible if “root-readable” means root-only. In this system unit the privileged service manager reads EnvironmentFile and injects environment variables before starting the User= process; the application need not have file read permission. State that application consumes environment variables, and revise the exercise to diagnose manager failure loading EnvironmentFile separately from application failure consuming configuration. Do not encourage granting application read access merely to fix EnvironmentFile startup. If direct file parsing is instead intended, explicitly give an appropriate restricted group mode and separate that alternative from EnvironmentFile behavior.

No other material finding. mv -Tf renames the symlink rather than moving inside its target; same-directory/same-filesystem atomic directory-entry replacement is correctly limited, and restart/health/external state are distinct. Tar ownership/umask flags are correctly not presented as archive safety. Validation wrapper, approved input, protected parent paths and no arbitrary privileged tar/shell authorization are explicit. Static example does not implement the wrapper and discloses this. Root ownership/read-only service access and immutable releases support the boundary; package and MAC differences are qualified. Code rollback and schema compatibility warnings are sound.

Low — fixed current.next staging name: mention serialization and checking/cleaning a stale candidate link after failed deployment; ln otherwise fails safely, but retries need diagnosis. Low — summary Status remains drafting while body frontmatter is draft, and its open thread says complete chapter despite intended content being present. Align authoring metadata on next summary update.

## Primary evidence checked 2026-10-04

- [OpenSSH configuration](https://man.openbsd.org/sshd_config.5): included/effective settings, user and authentication controls.
- [Linux rename](https://man7.org/linux/man-pages/man2/rename.2.html): symlink replacement, existing target atomicity and cross-mount EXDEV.
- [Official systemd.exec source](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.exec.xml): EnvironmentFile manager execution-environment semantics, User and WorkingDirectory.
- Local GNU mv/tar --help checked non-mutating: -T no-target-directory, -f force, no-same-owner extraction identity and no-same-permissions umask. Official GNU web manuals timed out and freedesktop systemd rendered manual returned403; accessible upstream systemd source used instead. No claim of exhaustive external-link validation.

## Validation and limits

`python3 tools/check_book.py --chapters 132-132` passed: four shell syntax checks,1,406 global local links; no errors/warnings. No VPS, account, SSH session, package install, archive extraction, wrapper, unit validation/start, symlink switch, MAC policy, proxy or rollback tested. No Ubuntu/Fedora/RHEL runtime matrix inspected. Documentation and shell syntax cannot establish safe archive validation, permissions, service startup or end-to-end recovery. Only this separate review record written.

## Final bounded correction review — 2026-10-04

Original findings above retained as history, not remaining blockers. Inspected corrected service-contract paragraph, initial application assumptions, exercise3/answer3 and candidate-link operations explanation. EnvironmentFile now accurately has the privileged system service manager loading variables while the unprivileged process consumes its environment without file read permission. Diagnosis separates manager load failure from missing application settings and avoids printing secrets; direct-file parsing is a separate explicit permission design. The mechanism paragraph and exercise corrections are resolved. Per-service lock/CI concurrency and stale-link target inspection address the optional concurrency note. Remaining medium finding — initial service-contract paragraph still says the unprivileged binary “reads /etc/dispatchdesk/api.env,” contradicting the corrected paragraph and root-only file design. Change this assumption to consuming environment variables supplied by systemd. Current body hash recomputed with tools.promote_reviewed.body_hash and matches785b2cd9c57aff64cf4431c0c722a77e59278b3d708f17a9b637c58ca1906a7b.

`python3 tools/check_book.py --chapters 132-132` passed: four shell syntax checks and1,406 global local links, no errors/warnings. Earlier source evidence and runtime limits remain: no package, archive, service, SSH, switch, wrapper, lock or deployment execution. Only this review record changed.

## Final consistency check — 2026-10-04

The last introductory contradiction is corrected: binary consumes configuration variables supplied by systemd. Inspected every api.env/EnvironmentFile reference and configuration-variable explanation; manager loading, process consumption, root-owned file permissions and separate direct-file alternative are now consistent. All original material findings are resolved; earlier findings and intermediate checks above are retained as historical scope. Current hash matches29da7c23bdacfa1bb03db4c4de13631a75de4993a80765a1c6e30ccc8e72d993. Focused checker again passed four shell syntax checks and1,406 global local links with no errors/warnings. No runtime test or new infrastructure action; prior limits remain. Only this separate review record updated.

Verdict: approved
