---
book: The Complete DevOps Engineering Book
volume: 6
volume_title: "Docker in Practice"
chapter: 53
title: "Dockerfiles and Build Contexts"
slug: dockerfiles-and-build-contexts
status: complete
summary: ../../_ai/chapter-summaries/053-dockerfiles-and-build-contexts.md
---

# Chapter 53 — Dockerfiles and Build Contexts

A Dockerfile describes how an image is assembled. The build context is the set of files the builder may read. The Dockerfile defines software and defaults; the context determines which application files and accidental secrets are available. Reliable images start with a clear project boundary, not a sequence of commands typed on a server.

We will package a tiny Python HTTP service for the fictional DispatchDesk API. It is instructional code, not a production web framework. The same build-context and instruction principles apply to PHP, Go and JavaScript.

## Instructions, context and ignore rules

Create a directory containing `.dockerignore`, `Dockerfile` and `app.py`. The app serves one health response on port 8080 and listens on all container interfaces:

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            body = b"ok\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

if __name__ == "__main__":
    address = os.environ.get("LISTEN_ADDR", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    HTTPServer((address, port), Handler).serve_forever()
```

The code omits order handling, TLS, persistence and graceful shutdown. It demonstrates image construction and networking, not production readiness. [The Container Contract](../05-container-internals-and-oci/050-the-container-contract.md) covers runtime expectations for a real service.

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --chown=10001:10001 app.py ./app.py
USER 10001:10001
EXPOSE 8080
CMD ["python", "app.py"]
```

`FROM` selects the base filesystem and interpreter. This tag is convenient for learning but can resolve to changing bytes; production builds should record a reviewed base digest. The official Python image documentation describes the variants. `ENV` sets inherited defaults. `WORKDIR` sets the location for later instructions. `COPY` takes a file from the context; `--chown` assigns numeric ownership. `USER` sets the identity for later build steps and the default process. `EXPOSE` documents a container port but does not publish it on the host. Exec-form `CMD` supplies the default process without an intervening shell.

Use an ignore file to exclude local material:

```text
.git
.venv
__pycache__
*.py[cod]
.env
.pytest_cache
```

Patterns apply relative to the context root. Tailor them: excluding a compiler input breaks the build; including credentials may send them to a remote builder or allow `COPY . .` to put them in an image. Ignore rules are not secret management. Use BuildKit secrets for build-only credentials, covered in [chapter 54](054-buildkit-caching-and-multi-stage-builds.md), and a runtime secret system for application credentials.

From the project directory, build the image:

```bash
docker build --tag dispatchdesk-api:dev .
```

The final `.` selects the context. The build requires a functioning daemon, these files and network access if the base is not cached. A remote builder receives the selected context, not arbitrary workstation files. Review context transfer size: an unexpectedly large transfer often includes generated output, dependencies or repository history.

Inspect the local image:

```bash
docker image inspect dispatchdesk-api:dev --format '{{.Id}} {{.Os}}/{{.Architecture}} {{json .Config.User}}'
docker image history dispatchdesk-api:dev
```

These commands show metadata and history, not security or reproducibility. A build can succeed with unwanted files or the wrong target platform. Run application tests and image policy checks before promotion.

## Layers and reproducible dependency installation

Filesystem changes from Dockerfile instructions are stored in layers that the builder may reuse. If an instruction's inputs and configuration are unchanged, a later build can reuse its result; changing an early input can invalidate following work. [Chapter 54](054-buildkit-caching-and-multi-stage-builds.md) explains cache behavior. A common pattern is to copy stable dependency inputs before frequently changed source when that matches the project.

For Python, copy project metadata and the lockfile, install the locked dependency graph, then copy application code. For JavaScript, copy `package.json` and its package-manager lockfile before source, then use that manager's lock-enforcing install command. Check exact flags against the project tool. A lockfile records the chosen dependency graph; deleting it to make a build pass hides a defect.

A lockfile does not pin the base image or operating-system packages. A base digest does not pin packages fetched from an unversioned repository. Production records should capture source revision, build parameters, base identity, lock state, target platform and output digest. Update pins through review so they do not become forgotten vulnerabilities.

Do not put credentials in Dockerfile `ARG` or `ENV` to access private dependencies: values may appear in logs or image metadata. Use a temporary BuildKit secret or SSH mount and ensure no instruction copies it into a layer. Copy only required files instead of blindly copying the whole repository. Group installation commands clearly; understandable, reproducible contents matter more than minimizing layer count. Multi-stage builds keep compilers and test tools out of runtime images; chapter 54 covers that boundary.

## Building a useful application image

On a disposable Docker host, run these commands in the project directory. Confirm the active context points to the intended daemon. With a remote context, the daemon builds and runs remotely; execute `curl` on the machine that owns the published loopback port.

```bash
docker build --tag dispatchdesk-api:dev .
docker run --detach --name dispatchdesk-api-lab --publish 127.0.0.1:18081:8080 dispatchdesk-api:dev
```

Then test and inspect it:

```bash
curl --fail --show-error http://127.0.0.1:18081/healthz
docker logs dispatchdesk-api-lab
```

The process runs as UID:GID 10001, listens on container port 8080 and maps to host loopback port 18081. Docker publication can interact with firewall rules; verify the actual host as explained in [chapter 51](051-installing-and-inspecting-docker.md). A successful request should return `ok`; no output is claimed as measured. If a command fails, capture the state and logs before cleanup. When finished, remove only this named lab container:

```bash
docker stop dispatchdesk-api-lab
docker rm dispatchdesk-api-lab
```

The commands remove the container and writable layer, leaving the image cached. If the builder cannot find `app.py`, check the working directory, context argument and ignore rules. If transfer is unexpectedly large, inspect generated files before deleting anything. If the process exits, inspect state, exit code and logs; confirm the image contains the script and that `CMD`, interpreter and port agree. If it runs but the request fails, compare the listen address and port with the container side of the mapping.

This development image has an interpreter, app file, non-root identity, documented port and explicit command. It does not include dependency isolation, scanning, resource bounds, secrets or provenance. A production image is a reviewed artifact with known inputs and an operational contract.

## Exercises and review questions

1. What does the final `.` select? How can you select another Dockerfile while retaining the context?
2. Why does `EXPOSE 8080` not publish a host port?
3. Which ignore rule excludes `.env`, and why is that not a full secret control?
4. A remote builder lacks a file that exists locally. What context evidence would you inspect?
5. How should a process running as UID 10001 receive a writable cache without running as root?

### Answer guidance

1. It selects the context root. `--file path/to/Dockerfile` selects another Dockerfile; ordinary `COPY` still cannot access files outside the context.
2. `EXPOSE` records metadata. A runtime mapping or other network path and compatible firewall policy are still needed.
3. `.env` excludes that exact file, but credentials can exist under other names or in source. Keep them out of context and use a secret manager.
4. Check the context path, ignore patterns and builder transfer details; remote builders see only the submitted context.
5. Make only the required cache directory writable by that UID or configure a suitably owned volume. Check host ownership and SELinux labels while preserving least privilege.

## Takeaways

- Keep the build context small and exclude local secrets and generated files.
- `EXPOSE` documents a port; it does not publish one.
- Lockfiles and base digests control different inputs; record and update pins deliberately.
- A successful build is not an application test. Run the image and retain useful failure evidence.

## Further reading

- [The Container Contract](../05-container-internals-and-oci/050-the-container-contract.md) — process and state expectations.
- [Running and Managing Containers](052-running-and-managing-containers.md) — lifecycle and port mappings.
- [BuildKit, Caching and Multi-stage Builds](054-buildkit-caching-and-multi-stage-builds.md) — secrets, caching and build stages.

## Sources and verification

Docker's [Dockerfile reference](https://docs.docker.com/reference/dockerfile/), [build context guide](https://docs.docker.com/build/concepts/context/), [build best practices](https://docs.docker.com/build/building/best-practices/), [build secrets guide](https://docs.docker.com/build/building/secrets/) and the [official Python image documentation](https://hub.docker.com/_/python) were inspected on 2026-10-02. The `python:3.12-slim` tag was available on that date; tags and package contents can change. Examples were reviewed but not built or run because this workspace has no Docker daemon.
