---
book: The Complete DevOps Engineering Book
volume: 4
volume_title: "VPS and Server Operations"
chapter: 31
title: "Choosing and Provisioning a VPS"
slug: choosing-and-provisioning-a-vps
status: complete
summary: ../../_ai/chapter-summaries/031-choosing-and-provisioning-a-vps.md
---

# Chapter 31 — Choosing and Provisioning a VPS

## Why this matters

Harbor needs a home for the first DispatchDesk API. The cheapest advertised virtual server can still be a poor fit if its disk is slow, its region adds latency to a managed database, or operators cannot reach a recovery console after a firewall mistake. Choosing a VPS means choosing a resource contract, failure boundary and operating responsibility, not only a monthly price.

This chapter turns the requirements from [Chapter 2](../01-engineering-mental-models/002-requirements-before-tools.md) into a small-server decision, then follows a generic first-boot process. Provider plans, prices, quotas and regional capabilities change; verify them in the provider's own current documentation before creating billable resources. Nothing in this chapter provisions a server.

## Size around the workload and failure objective

Start with the process the server must run, its dependencies and the way demand arrives. DispatchDesk's initial fictional scenario handles about one order request per second typically and ten at peak. Those figures are learning assumptions, not measurements. The API, database, worker, operating system and observability agent all consume CPU, memory, storage and network capacity. Estimate from a representative load test and real application measurements before selecting a plan.

A plan labelled with a certain vCPU count does not by itself guarantee sustained CPU performance. Providers may use shared cores or dedicated allocations and can describe these differently. Compare burst behavior, CPU steal or throttling evidence, memory limits, disk performance and network throughput under the intended workload. Avoid treating different providers' advertised units as directly equivalent.

Memory sizing includes the kernel, page cache, application runtime, database, background jobs and temporary migration overhead. A host that fits only at average demand can fail during a deploy when two versions, package updates or database maintenance overlap. Leave measured headroom and define which work sheds load first. Do not reserve so much unused capacity that the budget forces riskier recovery choices.

Choose the storage type and capacity from data volume, write pattern, growth and recovery needs. A small boot volume can fill with package caches, logs or database WAL before the application dataset looks large. Confirm whether provider volumes offer independent durability, snapshots, resizing and restore behavior. A snapshot attached to the same account and region is useful for some mistakes but is not automatically an independent backup.

Place the server near its users and important dependencies, while considering data residency, provider availability, operational support and network paths. A nearby region can reduce round-trip time, but an application and database in different regions may add more latency than users experience at the edge. Do not choose a second region without deciding how replication, failover, writes and recovery will work.

Write down the service objective and the failure it must survive. One VPS can be appropriate for a small team with an explicit restore path and accepted host-level downtime. It cannot survive loss of that host without recovery elsewhere. Adding a second host introduces synchronization, deployment, firewall, monitoring and data-consistency work; it is a response to a requirement, not an automatic marker of maturity. See [Harbor's VPS path](../20-architecture-and-platform-engineering/191-monoliths-services-and-organizational-boundaries.md) and the later [single-VPS project](../21-projects-and-industry-case-studies/201-dispatchdesk-on-a-single-vps.md) as the book develops them.

## Compare regions, resources and provider controls

Compare a short list of plans against actual requirements. Include CPU allocation policy, RAM, volume performance, transfer allowances, IPv4/IPv6 availability, private networking, backup controls, recovery console, image refresh cadence, API access, support path, status reporting and billing behavior. Record the date and source of every provider-specific assumption. Do not rely on a marketing page's current plan name after the purchase; capture the selected plan and its operative contract.

An hourly rate is not a total cost. Include attached storage, snapshots, public addresses, outbound data, backups, support tiers, taxes and idle resources. Estimate a month from the provider's billing rules, and set a budget alert where available. Alerts may arrive after usage begins and are not a hard spend cap. A shutdown server may still incur storage or reserved-resource charges; verify the provider's billing behavior.

Confirm the access and recovery controls before provisioning: where console access is exposed, how operator identities authenticate, whether audit logs exist, and how to regain service if cloud-init or SSH configuration fails. The console is a privileged path and should use individual accounts and multifactor authentication where supported. Protect API credentials outside the server and grant the minimum permissions needed to create, inspect and remove the intended resources.

Treat a provider image as an input with an owner and lifecycle. Check the operating-system release, architecture, image publisher, update model, cloud-init behavior and support policy. Avoid an old hand-built image with unknown SSH keys or stale packages. A reproducible build should identify its source image and record the initialization data that transforms it.

Before you click Create, review region, image, CPU/RAM, disk, network exposure, identity, initialization data, backup selection and estimated bill. In a practice account, use a tagged disposable resource and record its identifier. Creating a public virtual machine and optional volumes can incur charges immediately; deleting the instance may permanently erase data. Never paste real credentials into a book's shell history or user-data example.

## Bootstrap with cloud-init without hiding ownership

Cloud-init consumes provider metadata and user-data to initialize many Linux cloud images. A data source supplies the instance identity and configuration inputs; exact support differs by provider and image. Modules can run once per instance or at other frequencies. Re-running a boot script is not equivalent to reconciling desired state. Inspect the image's cloud-init documentation and logs, then keep durable configuration in the tool that owns it. [Cloud-init user-data formats](https://cloudinit.readthedocs.io/en/latest/topics/format.html).

This illustrative cloud-config creates an `ops` account whose access relies on a complete public key. Replace the placeholder with a public key under your control before using the file. User-data can be visible through provider control planes, logs or instance metadata; do not put passwords, private keys or long-lived tokens in it.

```yaml
#cloud-config
users:
  - default
  - name: ops
    shell: /bin/bash
    lock_passwd: true
    sudo: ["ALL=(ALL:ALL) NOPASSWD:ALL"]
    ssh_authorized_keys:
      - ssh-ed25519 REPLACE_WITH_COMPLETE_PUBLIC_KEY
ssh_pwauth: false
disable_root: true
```

The account has full passwordless sudo, so this key is root-equivalent access and the provider account that supplies the configuration is part of the trust chain. Use a controlled key and narrow the sudo policy to your organization's requirements before production. The public key string must be syntactically complete and the matching private key must remain with its owner. `lock_passwd` prevents password authentication for this account while allowing the configured key path; it does not lock the user account itself. `ssh_pwauth: false` asks cloud-init to disable SSH password authentication where the image supports it. `disable_root: true` disables direct root SSH login through the supported cloud-init configuration. Validate both effective SSH settings and actual key access after first boot; image-specific SSH configuration can override assumptions.

If cloud-init is installed locally, validate the cloud-config structure before attaching it to an instance:

```bash
cloud-init schema --config-file cloud-config.yaml
```

The schema check catches some input problems. It cannot prove a provider supplies the expected data source, that a key works, or that firewall and SSH access are correct. Preserve the exact rendered input, instance identifier, cloud-init status and logs as build evidence. Never retry a first-boot script blindly if it performs non-idempotent actions such as appending accounts or rotating keys.

## Build a first server with an auditable sequence

Use the provider's supported control plane from an authorized operator account. Select the approved image and region, attach only the required disk, supply the reviewed public-key/user-data configuration, and open only the intended network paths. Tag the instance with an owner, purpose and expiry or review date. Record the provider resource ID and configuration before making application changes.

After creation, confirm the instance reaches its expected state in the provider console and review its system console output. On a Linux client, connect using the verified host key procedure from [Chapter 26](../03-networking-and-traffic/026-ssh-and-remote-administration.md). Do not accept an unknown fingerprint simply because the provider created the server. If the provider exposes the fingerprint in a trusted console, compare it over that separate channel.

On the new host, verify the operating-system release, identity, addresses, routes, listeners, cloud-init completion and update state before installing the application:

```bash
cat /etc/os-release
id
ip -brief address show
ip route show
ss -ltn
cloud-init status --long
```

`/etc/os-release` confirms the image's distribution and version. `id` confirms the login identity and groups. Network and listener output establish host state, not provider firewall behavior. `cloud-init status --long` is useful on images that use cloud-init; absence of the command is not proof that provisioning failed. Read cloud-init logs if status is degraded, redact metadata and secrets before sharing, and repair the input at its owning source.

Apply the access baseline in Chapter 32, then configure monitoring, time synchronization, patch policy, recovery access and backups before deploying DispatchDesk. Check the provider's billing console and create an explicit teardown or retention decision. A server that is merely powered off can continue to incur storage or address charges.

## Diagnose an inaccessible first boot

The new host appears in the provider console, but SSH times out. Determine whether the VM booted, whether the expected interface and address exist, whether the provider's ingress policy permits the operator's source, and whether the host firewall permits SSH. Use the provider's serial or web console before editing remote networking. A timeout alone does not identify which layer dropped the connection; follow [Chapter 30](../03-networking-and-traffic/030-network-troubleshooting-in-layers.md).

If the console shows cloud-init failed to parse user-data, keep the instance isolated, inspect the relevant log and correct the source configuration. Rebuild a disposable learning instance when its first-boot state is uncertain rather than accumulating undocumented manual repair. For a production host, preserve required data and follow the provider's documented recovery procedure before replacing it.

If a key is rejected, verify the account name, public-key installation, private-key selection, file ownership and SSH daemon policy. Do not enable password login to bypass an unknown key error. If a firewall rule blocks the management path, repair the narrow source-specific rule through the provider control plane or console and retest a fresh SSH session. Record which layer failed and add a validation step to the next build.

## Exercises, review questions and takeaways

1. Compare two fictional VPS plans for the DispatchDesk scenario. Guidance: include sustained CPU, memory headroom, disk behavior, region, backups, recovery console and whole-month cost, then label every assumption.
2. Review the cloud-config. What would you replace, and where could the user-data be visible? Guidance: supply a complete public key and account for provider metadata/control-plane access; never add a private key or password.
3. Design the first-boot acceptance record. Guidance: capture image identity, resource ID, access test, host fingerprint, cloud-init status, network/listener evidence, patch state and billing owner.
4. Trace an SSH timeout. Guidance: check provider state, address/route, provider policy, host firewall, listener, key identity and logs in order, using console recovery.

Review questions: What does a provider snapshot fail to guarantee as a backup? Why are CPU labels not a cross-provider performance benchmark? Which first-boot tasks belong in cloud-init and which need ongoing reconciliation? Good answers identify recovery objectives, measured workload and configuration ownership.

Choose a host by its measured workload and recovery contract, then preserve a repeatable record of how it was built. Continue to [Chapter 32](032-host-hardening-and-access.md) to reduce exposure while preserving operator access.
