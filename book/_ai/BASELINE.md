# Version and environment baseline

Established: 2026-10-01. This date is a writing reference, not proof that any particular release is supported.

## Reader environments

- Ubuntu: use Ubuntu 24.04 LTS as the established baseline, with 26.04 LTS notes when relevant. Both are listed in [Canonical's release-cycle table](https://ubuntu.com/about/release-cycle), inspected on 2026-10-01. Record the actual release when package or security behavior matters.
- Fedora: use Fedora Server 44, offered on the [official download page](https://fedoraproject.org/server/download/), inspected on 2026-10-01. Verify package and networking behavior separately from RHEL; recheck Fedora support at future writing dates.
- RHEL: use supported RHEL 9, with RHEL 10 differences identified explicitly. The [Red Hat lifecycle policy](https://access.redhat.com/support/policy/updates/errata), inspected on 2026-10-01, covers these major-release families. Minor-release coverage and Application Streams must be checked separately. Explain subscription/repository requirements and give Rocky/AlmaLinux notes where appropriate.
- Shell: Bash examples on Linux; explicitly mark POSIX sh differences. macOS/Windows readers use Linux VMs or WSL where needed; native compatibility is not assumed.
- AWS: CLI v2 semantics; reader-selected profile and region, verified identity, explicit permissions, tagged disposable resources and teardown. No cloud resources are provisioned by the writing process.
- Kubernetes, Podman, Docker, Terraform/OpenTofu, CI and telemetry tooling: exact flags and API versions require per-chapter official documentation verification. Avoid an invented universal version pin.

## Authoring environment actually inspected

`git`, `curl`, Python 3, Podman, Node.js and Ruby executables are available. Docker, kubectl, AWS CLI, Terraform/OpenTofu and ShellCheck were not found during the initial check. An available executable does not prove its daemon, container engine, cluster or cloud account works.

Actual tool versions and successful execution checks will be recorded here or in chapter verification notes when measured. Do not label syntax-checked snippets as live-tested deployments.

## Measured on 2026-10-01

- Python: `Python 3.14.7` from `python3 --version`.
- Podman: `podman version 6.1.2`, inspected outside the sandbox. The sandbox attempt could not access the user runtime configuration; no container execution has been verified by this check.
- PyYAML and Python Markdown modules are available. The book validator uses PyYAML for parsing only, not Kubernetes, Compose, GitHub Actions or cloud schema validation.
- PHP reference checkout commit: `f813cd66e51f0dcba4b20db3fbb38ccfc89bb067`, cloned through SSH. The book structure is attributed to that repository, not copied wholesale.
- Additional language tools: PHP CLI 8.5.11, Node.js v26.10.0 and Go `go1.27.1-X:nodwarf5 linux/amd64` are installed. `gofmt`, jq and OpenSSL are available. The authoring validator can parse/lint complete inline language examples without executing them; Go formatting diagnostics are syntax evidence, not a full dependency build.
