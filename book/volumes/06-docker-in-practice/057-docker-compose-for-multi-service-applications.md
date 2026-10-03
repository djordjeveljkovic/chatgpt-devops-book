---
book: The Complete DevOps Engineering Book
volume: 6
volume_title: "Docker in Practice"
chapter: 57
title: "Docker Compose for Multi-service Applications"
slug: docker-compose-for-multi-service-applications
status: complete
summary: ../../_ai/chapter-summaries/057-docker-compose-for-multi-service-applications.md
---

# Chapter 57 — Docker Compose for Multi-service Applications

DispatchDesk is no longer one process. Its HTTP API, background worker, PostgreSQL database and Redis cache have separate lifecycles, but developers still need one repeatable way to start and inspect the stack. Docker Compose describes those services, their networks, configuration and storage in a YAML application model. It helps operate a group of containers on one Docker host; it does not turn that host into a scheduler, database cluster or production control plane.

This chapter uses Docker Compose v2 (`docker compose`) with a local Linux Docker Engine on a disposable host. The example is an orchestration lab: its small API returns a health response but does not issue SQL or Redis commands, and its worker waits as a placeholder process. The database and cache run and can be tested separately. This separation makes Compose behavior visible without pretending the sample application already implements DispatchDesk's data flows. For service discovery and data lifecycles, see [Chapter 55](055-docker-networking.md) and [Chapter 56](056-docker-volumes-and-persistent-data.md).

## Services, networks and configuration

Compose files define services, not individual container IDs. A service describes the image or build, command, environment, network attachments, storage and other runtime settings. Compose creates containers from that model and labels them with a project identity. By default, services join a project network and can reach each other using service names such as `db` and `cache`; their IP addresses are implementation details. A service name provides discovery, not authentication or encryption. Do not publish database ports merely so another container can reach them.

Create a new project directory on the Docker host, then save the following four files as `compose.yaml`, `Dockerfile`, `app.py` and `.dockerignore`. Keep `.local-secrets/` out of version control and out of every image build context. These are separate controls: ignoring a build-context path does not prevent Compose from mounting that file as a runtime secret. The Compose file intentionally has no deprecated top-level `version` field: current Compose uses the Compose Specification.

`.dockerignore`:

```text
.local-secrets/
.git/
__pycache__/
*.py[cod]
```

This file prevents local secret material and repository internals from being sent as part of this project's Docker build context. Add other sensitive or generated paths deliberately; do not exclude application inputs the Dockerfile needs. A `.dockerignore` file is not a substitute for carefully scoped `COPY` instructions or access control on the source files.

`compose.yaml`:

```yaml
services:
  api:
    build: .
    image: dispatchdesk-compose-api:dev
    ports:
      - "127.0.0.1:18082:8080"
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 5s

  worker:
    image: dispatchdesk-compose-api:dev
    command: ["python", "-c", "import time; time.sleep(86400)"]
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: dispatchdesk
      POSTGRES_USER: dispatchdesk
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \"$${POSTGRES_USER}\" -d \"$${POSTGRES_DB}\""]
      interval: 5s
      timeout: 3s
      retries: 12
      start_period: 10s

  cache:
    image: redis:7.4-alpine
    command: ["redis-server", "--save", "", "--appendonly", "no"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 12
      start_period: 5s

volumes:
  db-data:

secrets:
  db_password:
    file: ./.local-secrets/db-password
```

`Dockerfile`:

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY app.py ./app.py
USER 10001:10001
EXPOSE 8080
CMD ["python", "app.py"]
```

`app.py`:

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/healthz":
            self.send_error(404)
            return
        body = json.dumps({"status": "ok", "mode": "compose-lab"}).encode() + b"\n"
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
```

The API and worker use the same local image: the API runs the image's default HTTP process, while the worker overrides the command with a long sleep. That worker exists only to show independent service lifecycle and shared dependencies; it does not consume a queue. The API health check verifies only that its HTTP handler responds. Neither check proves business behavior or a connection from the app to the database. The `db-data` named volume retains PostgreSQL files when the database container is replaced; see [Chapter 56](056-docker-volumes-and-persistent-data.md) for backup and restore boundaries.

Create a disposable lab password file with restrictive permissions. This command uses local Python to generate a random value; it prints nothing to the terminal, and the secret file must remain excluded from source control:

```bash
umask 077
mkdir -p .local-secrets
python3 -c 'import secrets; print(secrets.token_urlsafe(32))' > .local-secrets/db-password
```

Compose file secrets grant a service access to a file at `/run/secrets/db_password`; the `db` service alone receives it. With standalone Compose, the source file remains on the host and this mechanism is a controlled file mount, not a remote secrets vault or Swarm's encrypted secret store. Protect the host file and backups, and use an environment-appropriate secret manager for production. The Postgres image reads `POSTGRES_PASSWORD_FILE` during first-time database initialization. Changing that file later does not rotate the password in an already initialized database. A real rotation requires coordinated database and client changes.

On Fedora/RHEL with SELinux enforcing, file-backed Compose secrets are read-only bind mounts and can be denied by the host label even if Unix permissions allow the database entrypoint to read the file. For a dedicated local lab secret and a Compose version that supports the Compose Specification's bind `selinux` option, replace the `db` service's `secrets: - db_password` grant with this bind entry in its existing `volumes:` list:

```yaml
      - type: bind
        source: ./.local-secrets/db-password
        target: /run/secrets/db_password
        read_only: true
        bind:
          selinux: Z
```

Remove the now-unused top-level `secrets:` declaration for `db_password`. `Z` requests a private label for this one container; `z` is for content intentionally shared by multiple containers. The source is a single dedicated file, and the target remains the exact path expected by the image. Keep mode `0600`; SELinux labeling does not replace ordinary file permissions. Check `docker compose version` and `docker compose config --quiet` before starting because older implementations may not accept this Compose Specification option. Do not turn off SELinux to work around a denial. If the host still blocks access, inspect `getenforce`, `ls -lZ .local-secrets/db-password` and recent AVC audit records, then correct the narrowly scoped host policy. This variant changes host file labeling and must not be aimed at a broad directory or shared production secret.

`POSTGRES_DB` and `POSTGRES_USER` select the initial database and role for a fresh data directory. Initialization variables do not reconfigure an existing `db-data` volume. Redis is deliberately configured without RDB snapshots or append-only persistence because this example treats it as a disposable cache. Do not copy that setting if Redis stores queues or authoritative state. PostgreSQL's named volume keeps the database state across Compose container recreation on this daemon, not across disk or host loss. Back it up using database-aware procedures.

The host port is bound to loopback so a local test client can reach the API without deliberately listening on every host interface. The database and Redis have no published host ports. All four services can still communicate on Compose's default project network. If the active Docker context is remote, commands act on that daemon and `127.0.0.1:18082` refers to the remote daemon host; run `curl` there or use a deliberately configured access path. Check host firewall and Engine publication behavior before any shared-host use.

## Dependencies and readiness

Compose creates dependencies in order. Short-form `depends_on` waits for a dependency container to start, not for its service to be ready. The long form used above requests `service_healthy`, so Compose waits until the dependency's configured health check passes before starting the dependent service. PostgreSQL's `pg_isready` checks whether the server accepts connections; Redis's `PING` checks whether Redis responds. They do not test API credentials, schema, permissions, application queries, data correctness or network policy outside this Docker host.

Readiness is still a momentary observation. A database can restart after the API starts, a query can fail despite a healthy process, and a network partition can interrupt established connections. Real applications need bounded connection timeouts, retry with backoff and jitter where safe, a clear behavior when retries end, and idempotent handling around work that may be repeated. `depends_on` is startup ordering, not continuous supervision of application dependencies. Container health status also does not automatically restart a container; pair restart policy and health semantics thoughtfully, and alert on meaningful application symptoms.

The health checks must use tools that actually exist in their images. This API image includes Python's standard library, so its check uses `urllib`; the Postgres image provides `pg_isready`; Redis provides `redis-cli`. A check that calls `curl` in an image without curl reports failure even when the service works. The probe's interval, timeout, retry count and start period shape detection delay and load. Keep probes cheap and representative, and avoid turning a remote dependency outage into a restart storm.

Compose interpolates `$` expressions in YAML before passing configuration to containers. The doubled dollar signs in the database health check (`$${POSTGRES_USER}`) preserve the variable reference for the container shell; a single `$` would be interpreted by Compose using the operator's environment. Use `.env` only for non-secret configuration that is safe to store locally. Run `docker compose config` to inspect the rendered model, but review its output before sharing because interpolated values can be sensitive.

## Bring up and inspect an API, worker, PostgreSQL and Redis stack

Run these commands from the directory containing the three files and `.local-secrets/db-password`. Confirm the current context with `docker context show`; use only a disposable host. `docker compose config --quiet` validates the merged model without starting containers. Then build and start the project:

```bash
docker context show
docker compose config --quiet
docker compose up --build --detach
```

`--build` builds the local API image from the current directory, and `--detach` leaves the services running. The first run may pull Python, Postgres and Redis images and initialize database files in a new named volume; it needs registry/network access, disk space and a free local port 18082. Tags such as `postgres:16`, `redis:7.4-alpine` and `python:3.12-slim` can move as publishers update them. They are learning references. A production release should review supported versions, record immutable image digests and make upgrades deliberately.

Inspect service state and recent logs:

```bash
docker compose ps
docker compose logs --tail 50 api worker db cache
```

Depending on how quickly the stack starts, the database and cache should become healthy before Compose starts the API and worker. The API should become healthy after its own HTTP probe passes. These states are illustrative expectations, not output measured in this workspace. If `db` remains unhealthy, inspect its logs and configuration before removing data. A reused database volume may have old initialization state or incompatible data. If `api` does not start, check image build output, health status, logs and port conflicts. If the CLI connects to a different daemon context than expected, its `ps` and logs are evidence about that selected daemon only.

Test the endpoint on the machine that owns the published loopback port and inspect the dependency probes:

```bash
curl --fail --show-error http://127.0.0.1:18082/healthz
docker compose exec db pg_isready -U dispatchdesk -d dispatchdesk
docker compose exec cache redis-cli PING
docker compose exec api python -c 'import socket; print("db", socket.gethostbyname("db")); print("cache", socket.gethostbyname("cache"))'
```

The HTTP handler returns a small JSON health response; no database query is made by the API. `pg_isready` confirms a PostgreSQL server is accepting connections for that database/user combination but does not prove that a normal application login can query its schema. Redis should answer `PONG`. The final command checks that the API container resolves the two Compose service names to current addresses. IPs may change after recreation, so the configuration should use names. For a real DispatchDesk release, add an authenticated application query and a worker job that records observable completion before declaring end-to-end success.

Compose project naming affects generated container, network and volume names. By default, Compose derives the project name from the directory; `-p` or `COMPOSE_PROJECT_NAME` can select one explicitly. Two checkouts may therefore create distinct default volumes, while an accidental project-name collision can make them share unexpected resources. Use a stable, intentional project identity in automation and inspect `docker compose config --volumes` and `docker volume ls` before stateful operations. Do not add `container_name` simply to get stable service DNS; it constrains scaling and does not replace service discovery.

For a controlled replacement, recreate only the API after an image/config change:

```bash
docker compose up --build --detach --no-deps api
docker compose ps
curl --fail --show-error http://127.0.0.1:18082/healthz
```

`--no-deps` avoids restarting its database/cache dependencies for this limited example. It is appropriate only because those services already run and this API does not need a coordinated schema change. For actual releases, use an explicit migration and rollout plan; Compose does not guarantee zero-downtime replacement or coordinate incompatible schema versions.

When finished, stop the project:

```bash
docker compose down
```

This removes the project's containers and default network but preserves named volumes such as `db-data`. The local database state remains on the daemon. To delete the lab database as well requires an explicit destructive command, `docker compose down --volumes`; inspect the project identity and backups first. The lab secret file is also separate from Compose-managed state and must be deleted deliberately if no longer needed. For this disposable lab, remove the generated password file after shutdown when it is no longer needed; the private SELinux label applies only to that dedicated source path. Do not run `down --volumes` against an unknown project or production data directory.

## Troubleshoot dependency and lifecycle failures

If `docker compose up` reports that `db_password` is missing, confirm the working directory, source file path and file permissions. On an enforcing SELinux host, also inspect the file context and relevant AVC denial; with the base file-secret form, a labeling denial can prevent the entrypoint from reading the mounted file. Apply the Compose bind variant above to the dedicated lab file or follow the host's approved policy procedure. Preserve SELinux enforcement. If PostgreSQL initializes but clients see authentication errors after a password-file edit, remember that the initialized volume retains the old database credentials; update the role through a controlled database session and coordinate clients. Do not delete the volume as a shortcut when it may contain valuable data.

If the API starts before a dependency is usable, inspect the rendered `depends_on` conditions and dependency health checks. If it starts but later cannot connect, Compose ordering cannot repair the lost connection; inspect service logs, DNS, listener state and application retry behavior. A healthy Redis ping does not show that an application key exists. If service-name resolution fails, compare `docker compose ps` and `docker network inspect` against the selected project and confirm both services share a network. If an API health check fails, run its probe command inside the container and verify that the application listens on `0.0.0.0`, not only container loopback.

If the API answers on the host but cannot be reached externally, the current loopback binding is intentional. If an external port is required, choose a deliberate host address and port, then evaluate host firewall, cloud policy, TLS termination and authentication as a separate exposure decision. A container being on a private Compose network does not mean a published port is private.

## Exercises and review questions

1. Why does short-form `depends_on` fail to guarantee that PostgreSQL can accept a connection when the API begins?
2. What does the `db` health check establish, and what important application behavior does it leave untested?
3. The same Compose files run in two directories and each stack has an empty database. Which project and volume behavior could explain this?
4. An engineer edits `.local-secrets/db-password`, recreates the `db` container and the API still cannot authenticate. Why can this happen, and what is a safer response than deleting the database volume?
5. What resources does ordinary `docker compose down` remove in this example? What additional data-loss risk comes from `down --volumes`?
6. The API container is healthy, PostgreSQL is healthy and the worker is running, but a customer order does not process. Which evidence must be added to validate the business flow?

### Answer guidance

1. Short syntax waits for the dependency container to start, not its configured health state. Long syntax with `condition: service_healthy` gates dependent startup on the health check.
2. `pg_isready` checks that the server accepts connections for the supplied target. It does not prove the application's credentials, schema permissions, query semantics or business invariants.
3. The default project name derives from the directory, and generated named volumes are project-scoped. Distinct project names can produce separate database volumes. Confirm names with Compose config and daemon volume inspection before changing state.
4. The official image reads the password file during initial database creation; changing the host file does not rotate the stored role password. Use a controlled SQL role-password rotation, update the dependent client configuration, and verify authentication while retaining the data volume.
5. Ordinary `down` removes project containers and the default network while retaining named volumes. Adding `--volumes` deletes project-managed volume data, including PostgreSQL files in this lab.
6. Add application-level dependency connections, authenticated query evidence, a worker job identifier/status, logs or metrics for enqueue and completion, and an end-to-end test that verifies the persisted business record and resulting side effect.

## Takeaways

- Compose describes a multi-container application on a Docker host; it is not a multi-host scheduler or managed database service.
- Services share a project network and resolve one another by service name; publish only the ports that require a host path.
- `depends_on` ordering differs from readiness. Health checks can gate startup but do not provide continuous dependency recovery or business-level proof.
- Keep credentials out of committed files and understand that standalone Compose file secrets remain host files mounted into selected services.
- Named volumes survive ordinary project removal; volume deletion is a separate data-loss decision.
- A healthy set of containers does not prove the API, worker and database complete a customer workflow.

## Further reading

- [Docker Volumes and Persistent Data](056-docker-volumes-and-persistent-data.md) — data lifecycle and restore testing.
- [Inspecting and Debugging Docker](058-inspecting-and-debugging-docker.md) — evidence collection when a service fails.
- [Docker Networking](055-docker-networking.md) — service discovery, bridge behavior and published-port boundaries.
- [Database and Cache Operations on One Host](../04-vps-and-server-operations/036-database-and-cache-operations-on-one-host.md) — database durability and cache-role decisions.

## Sources and verification

Docker's [Compose service reference](https://docs.docker.com/reference/compose-file/services/), [startup order guidance](https://docs.docker.com/compose/how-tos/startup-order/), [secrets guide](https://docs.docker.com/compose/how-tos/use-secrets/), [SELinux bind mount labeling](https://docs.docker.com/engine/storage/bind-mounts/#configure-the-selinux-label), [build context and ignore files](https://docs.docker.com/build/concepts/context/#dockerignore-files), [`docker compose config`](https://docs.docker.com/reference/cli/docker/compose/config/), [PostgreSQL 16 Official Image source](https://github.com/docker-library/postgres/tree/master/16) and current [image tag listing](https://github.com/docker-library/official-images/blob/master/library/postgres) were inspected on 2026-10-03. The Compose Specification and image assumptions reflect that inspection date; the `postgres:16`, `redis:7.4-alpine` and `python:3.12-slim` tags are examples, not immutable identities. Commands and YAML were checked statically but no Docker daemon or live Compose stack was available, so no image pull, build, health transition, request, backup or teardown was executed.
