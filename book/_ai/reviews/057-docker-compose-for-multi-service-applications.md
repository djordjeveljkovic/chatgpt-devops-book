# Independent review — Chapter 57

Reviewer: review_055
Date: 2026-10-03
Verdict: approved
Reviewed body SHA256: d74bcc957297e2a3a657754bbdaffabc4624b61a56855dcf97c000fce63b644d

## Findings

No unresolved material findings.

The build-context finding is resolved by the complete `.dockerignore` excluding `.local-secrets/`, `.git/` and Python-generated files, with prose distinguishing build exclusions from version-control and runtime mount controls.

The SELinux finding is resolved by a Fedora/RHEL enforcing-host variant replacing the file-secret grant with a dedicated read-only bind to the same `/run/secrets/db_password` target and `bind.selinux: Z`. Instructions preserve the existing database volume, remove the unused secret declaration, retain restrictive Unix permissions, check deployed Compose support and rendered configuration, diagnose labels/AVCs, preserve enforcement and limit relabeling to the dedicated file. Cleanup addresses the generated secret separately from Compose state. Confirmed long-form `bind.selinux` syntax against the current [official Compose volumes reference](https://docs.docker.com/reference/compose-file/services/#volumes). No live relabel or access test was performed.

Re-read the repaired body, including source and cleanup additions. The remaining reference to “three files” in the bring-up paragraph is minor wording drift after adding `.dockerignore`; the explicit four-file setup establishes the prerequisite and no material ambiguity remains.

## Factual assessment

The chapter meets its ordered Compose sections and supplies a complete four-service model, Python HTTP probe and Dockerfile. The limited API and sleeping worker are explicitly described, so the lab does not falsely claim an implemented business workflow. Numeric non-root identity, Python standard-library HTTP health check, all-interface container listener, quoted loopback host mapping, unpublished dependency ports and default-network DNS are internally consistent. No Python dependency installation is hidden. Redis's empty `--save` value and disabled append-only mode correctly express a disposable cache. PostgreSQL 16's named-volume path is correct for the selected major version.

Long-form `service_healthy`, short-form startup ordering, health-state limitations, retries and the lack of automatic restart from unhealthy status are correctly distinguished. Escaped Compose dollar signs retain container-shell expansion. `pg_isready` does not prove an authenticated application query; the text and answers preserve that limit. The default local Unix-socket probe also does not validate the API-to-database TCP path. API health, Redis PING and service-name DNS evidence are appropriately bounded. The worker's 86400-second sleep is a lab placeholder, not continuous job processing.

File-backed secrets are correctly distinguished from a remote vault and Swarm's secret store. The Postgres entrypoint reads the password file, exports the resulting value and unsets the `_FILE` variable before dropping to the postgres user; restrictive host file mode alone is therefore not a demonstrated rootful startup bug. Initialization settings and password-file edits do not rotate an initialized role password. Named-volume retention and destructive `down --volumes` behavior, project identities, `container_name` scaling limits and selected-daemon evidence are accurately explained.

Current Compose source recognizes an image built by another service when handling a failed pull, so sharing the API image with an image-only worker is not treated as a proven startup failure. A prebuild or explicit pull policy could make the procedure quieter, but it is not a material finding. `up --build --detach`, `config --quiet`, inspection, targeted API update and teardown flags match their documented uses. The targeted update need not recreate an unchanged API, and the prose correctly ties it to an image/config change. The six exercises and answer guidance support the chapter outcomes. Failure and recovery reasoning protects database data and correctly separates private network membership from host publication. Relative links resolve; repetition is modest.

## Validation evidence and limitations

Read `AI_AUTHORING_GUIDE.md`, progress context, Chapter 57 brief, chapter and summary, relevant Chapter 56 prerequisite summary and the prior networking review context. Calculated the inspected body hash with `tools.promote_reviewed.body_hash`.

Inspected official primary sources on 2026-10-03: [Compose service reference](https://docs.docker.com/reference/compose-file/services/), [startup ordering](https://docs.docker.com/compose/how-tos/startup-order/), [secrets guide](https://docs.docker.com/compose/how-tos/use-secrets/), [Compose build specification](https://docs.docker.com/reference/compose-file/build/), [config CLI](https://docs.docker.com/reference/cli/docker/compose/config/), [up CLI](https://docs.docker.com/reference/cli/docker/compose/up/), [down CLI](https://docs.docker.com/reference/cli/docker/compose/down/), [Postgres entrypoint source](https://github.com/docker-library/postgres/blob/master/docker-entrypoint.sh), [PostgreSQL 16 image Dockerfile](https://github.com/docker-library/postgres/blob/master/16/bookworm/Dockerfile), [PostgreSQL 16 pg_isready](https://www.postgresql.org/docs/16/app-pg-isready.html), [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [Docker build context](https://docs.docker.com/build/concepts/context/), [bind mounts](https://docs.docker.com/engine/storage/bind-mounts/) and Docker Compose source files for [build](https://github.com/docker/compose/blob/main/pkg/compose/build.go), [pull](https://github.com/docker/compose/blob/main/pkg/compose/pull.go) and [mount creation](https://github.com/docker/compose/blob/main/pkg/compose/create.go). Source inspection is a snapshot of upstream main/master, not proof about every Compose v2 or historical image build.

Ran `python tools/check_book.py --chapters 57-57`: two YAML parsing checks, one Python syntax check, six shell syntax checks and 1,259 repository local-link checks passed with no errors or warnings on the final rerun after the coordinator repaired an unrelated Chapter 58 link. Manually checked YAML service/dependency references, Dockerfile path and user assumptions, commands and copied Python source. These checks do not substitute for a Compose schema/runtime check or executing the HTTP application.

No Docker/Compose invocation, image pull/build, HTTP/DNS request, database operation, secret use, firewall/SELinux change or teardown was executed. No live Compose model validation or enforcing-host access test was available. Image tag availability and actual health transitions remain untested. Both prior material findings are resolved. Approval covers the reviewed body and documentation/static evidence, retaining all runtime limits. This record was updated after the coordinator completed the summary replacement; the transient missing-summary error from the first rerun no longer occurs.
