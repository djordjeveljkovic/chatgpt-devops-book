---
book: The Complete DevOps Engineering Book
volume: 8
volume_title: "Infrastructure as Code"
chapter: 77
title: "Ansible Inventory and Playbooks"
slug: ansible-inventory-and-playbooks
status: complete
summary: ../../_ai/chapter-summaries/077-ansible-inventory-and-playbooks.md
---

# Chapter 77 — Ansible Inventory and Playbooks

## Inventory, modules, and tasks

Harbor owns two disposable Linux hosts for testing DispatchDesk's host configuration. One runs Ubuntu 24.04 LTS; the other runs Fedora 44 or entitled RHEL 9. The configuration should converge on an inspectable result without hiding the distributions' differences. Ansible supplies a controller-driven workflow: inventory identifies targets, a play selects hosts, and ordered tasks invoke modules that inspect and change those hosts.

The controller is the machine running Ansible. The managed host is the SSH target. Most ordinary Linux modules need a supported Python interpreter on the target; bootstrapping a host without Python is a separate preparation step. Use an installed, documented Ansible version on the controller and record it with `ansible --version`. Ansible's Python support matrix and the chosen distribution's available interpreter must agree. Installing a package named ansible is not proof that every example module exists in its bundled version.

Inventory names are operational identities, not necessarily DNS names. Save this complete `inventory.ini` in a new controller directory, replacing the documentation addresses with reachable disposable hosts and `operator` with each approved login:

```ini
[lab]
ubuntu_lab ansible_host=192.0.2.10 ansible_user=operator
rpm_lab ansible_host=192.0.2.11 ansible_user=operator

[lab:vars]
ansible_python_interpreter=/usr/bin/python3
```

The addresses are reserved documentation examples. They will not make this lab work unchanged. SSH keys and verified host keys must already be configured; do not disable host-key checking to conceal an unverified target. The operator needs approved sudo capability for host configuration. The inventory contains no private key or password.

A module describes a particular operation's desired result. A package module can ensure a package is present, a file module can establish a directory's mode, and a systemd module can start a unit. Use fully qualified module names so the source of behavior is unambiguous. A command task may be necessary, but it loses some inspection and convergence behavior unless its conditions and changed status are deliberately defined.

## Privilege, handlers, and idempotency

The controller normally runs as the reader's ordinary account. `become: true` asks Ansible to elevate on the target for tasks that need it; it does not require running the controller itself as root. Inventory login identity and become identity are distinct. A failed sudo authentication is not an SSH failure, and an SSH connection failure is not evidence that the package manager rejected a package.

A handler runs after notified changes, allowing several updated files to request one restart. This reduces unnecessary service disruption, but it is not a transaction or rollback mechanism. If a later task fails before handlers execute, a changed file can remain on disk while the old process still runs. Decide whether a workflow needs earlier handler flushing, validation before publication, or an explicit recovery block. The lab below flushes before checking health so the check observes the intended process version.

Idempotency is measured through both reported changes and actual behavior. Two runs can show no changes while a manually broken external dependency still prevents orders. Conversely, an unconditional restart can make every run disruptive even when configuration bytes are identical. Prefer resource modules, change-triggered handlers, and application-level checks. [Declarative reconciliation](071-declarative-infrastructure-and-reconciliation.md) explains the underlying ownership model.

## Configuring Ubuntu and Fedora/RHEL hosts

This lab deploys a deliberately small loopback HTTP health responder, not the production order API. It establishes a Python file, a system user, a systemd unit, and a verification request. It never listens on an external address or changes firewall policy. Do not use Python's standard-library HTTP server as an implied production service stack; the point is to observe configuration and restart behavior without a hidden application dependency.

Save this complete `health.py` on the controller beside the playbook:

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/healthz":
            self.send_error(404)
            return
        body = b"healthy\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

HTTPServer(("127.0.0.1", 8080), Health).serve_forever()
```

Save `dispatchdesk-health.service.j2` beside it:

```ini
[Unit]
Description=DispatchDesk Ansible health lab
After=network.target

[Service]
Type=simple
User=dispatchdesk-lab
ExecStart=/usr/bin/python3 /opt/dispatchdesk-lab/health.py
Restart=on-failure
RestartSec=2s
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true

[Install]
WantedBy=multi-user.target
```

The service runs as a non-login system user and needs no privileged port. The script is root-owned and read-only to the service. `ProtectSystem=strict` makes filesystem writes unavailable except deliberately permitted paths; this responder has no durable state requirement. Production DispatchDesk would need explicit data, logs, environment, and shutdown contracts as described in [systemd deployment](../04-vps-and-server-operations/034-deploying-a-service-with-systemd.md).

Save this complete `site.yml`:

```yaml
- name: Configure the isolated DispatchDesk health lab
  hosts: lab
  become: true
  gather_facts: true
  serial: 1
  tasks:
    - name: Require a supported Linux family for this lab
      ansible.builtin.assert:
        that:
          - ansible_facts.os_family in ['Debian', 'RedHat']
        fail_msg: This lab targets Ubuntu or Fedora/RHEL hosts.

    - name: Install the target Python runtime
      ansible.builtin.package:
        name: python3
        state: present

    - name: Create the service account
      ansible.builtin.user:
        name: dispatchdesk-lab
        system: true
        create_home: false
        shell: /usr/sbin/nologin

    - name: Create the application directory
      ansible.builtin.file:
        path: /opt/dispatchdesk-lab
        state: directory
        owner: root
        group: root
        mode: '0755'

    - name: Install the complete responder
      ansible.builtin.copy:
        src: health.py
        dest: /opt/dispatchdesk-lab/health.py
        owner: root
        group: root
        mode: '0644'
      notify: Restart health lab

    - name: Install the service unit
      ansible.builtin.template:
        src: dispatchdesk-health.service.j2
        dest: /etc/systemd/system/dispatchdesk-health.service
        owner: root
        group: root
        mode: '0644'
      notify: Restart health lab

    - name: Enable and start the service
      ansible.builtin.systemd_service:
        name: dispatchdesk-health.service
        daemon_reload: true
        enabled: true
        state: started

    - name: Apply notified changes before checking health
      ansible.builtin.meta: flush_handlers

    - name: Verify the host-local health response
      ansible.builtin.uri:
        url: http://127.0.0.1:8080/healthz
        status_code: 200
        return_content: true
      register: health
      retries: 5
      delay: 1
      until: health.status == 200
      when: not ansible_check_mode

  handlers:
    - name: Restart health lab
      ansible.builtin.systemd_service:
        name: dispatchdesk-health.service
        daemon_reload: true
        state: restarted
```

`serial: 1` operates on one host batch at a time, limiting simultaneous disruption in this example. It does not establish load-balancer draining or guarantee an availability target. The family assertion is a coarse guard, not proof of a supported release. Record actual facts and test Ubuntu, Fedora, and RHEL independently.

The generic package module selects the target package-manager implementation; it does not translate arbitrary package names. `python3` is intentionally a common runtime package in this example. Ubuntu uses APT repository policy; Fedora uses its own DNF/package baseline; RHEL requires enabled entitled repositories or an explicitly chosen compatible distribution. Updating package metadata, selecting streams, and pinning versions need platform-specific tasks. [Package module documentation](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/package_module.html) explains the abstraction's limits.

`/usr/sbin/nologin` must exist on the target; verify it before the account task if the image differs. Mandatory access control remains active. Fedora/RHEL SELinux and Ubuntu AppArmor can reject operations according to the actual domain/profile. Diagnose denials and labels using [host security](../04-vps-and-server-operations/032-host-hardening-and-access.md), rather than disabling protection. This lab does not claim to define a custom confined service domain.

## Run, inspect, and recover

From the controller directory, first inspect the selection and syntax:

```bash
ansible-inventory -i inventory.ini --list
ansible-playbook -i inventory.ini site.yml --syntax-check
ansible-playbook -i inventory.ini site.yml --check --diff --limit ubuntu_lab --ask-become-pass
```

`-i` selects the inventory, `--limit` narrows the host selection, and `--ask-become-pass` requests the target escalation password when required. Omit that option only when the approved sudo policy already permits the operation. Check mode predicts supported changes; it does not execute the complete service workflow. The health task is explicitly skipped in check mode because a new service may not exist yet. Diff can expose file content; use it only for nonsensitive files.

An authorized reader applies to the disposable Ubuntu host with `ansible-playbook -i inventory.ini site.yml --limit ubuntu_lab --ask-become-pass`, verifies the result, then repeats for `rpm_lab`. The second identical run should avoid file changes and handler restarts. Inspect the recap, then verify the actual target service and HTTP response. Ansible's URI request executes on the target, so loopback refers to the target host, not the controller.

For a failed start, SSH to that target and run `sudo systemctl status dispatchdesk-health.service --no-pager` and `sudo journalctl -u dispatchdesk-health.service -n 50 --no-pager`. The status command shows unit state; the journal selects that unit's recent fifty entries without a pager. A bind error suggests port 8080 is already occupied. Inspect listeners using the canonical [host diagnostics](../04-vps-and-server-operations/040-vps-incidents-and-capacity.md), identify the owner, and choose a deliberate free port in both code and verification. Do not kill an unknown process.

A copied Python syntax error is another realistic failure. The file task can succeed while the service fails. Recover by restoring the reviewed file, rerunning the playbook, and checking health. A production workflow should validate artifacts before promotion; this tiny lab exposes why successful file copying is weaker than successful process behavior. A task failure leaves prior host changes in place, so a rerun must be based on inspection rather than a belief that nothing happened.

Cleanup is explicit and destructive to lab assets only. Stop and disable the unit on each disposable target with `sudo systemctl disable --now dispatchdesk-health.service`, remove the named unit and `/opt/dispatchdesk-lab/health.py`, reload systemd, and remove the now-empty lab directory and account only after confirming they are unused. Do not remove Python merely because the lab installed it; other host software may depend on it. Keep cleanup separate from production service lifecycle.

## Exercises and answer guidance

1. Change the health response body and rerun twice. The first copy change should notify one restart; the second run should leave file content unchanged. Verify the actual response after the restart.
2. Why can a check-mode run report plausible changes without proving service startup? Supported modules predict modifications; the runtime and health check may be absent or deliberately skipped.
3. The Ubuntu host works and the RHEL host fails before package installation. What evidence comes first? Separate SSH, Python availability, sudo, repository entitlement, and policy denials from application behavior using the exact failed task and diagnostic.

Review questions: Where do controller files live? Where does a URI task execute? What triggers a handler? Why is generic package management not generic repository policy?

Ansible is effective when inventory selection is explicit, module changes have clear ownership, privilege is scoped to the target, and verification observes the process that the files were intended to configure.

## Sources and verification

Official Ansible package, template, playbook, CLI, user, systemd_service, and handler documentation was inspected 2026-10-01. The modules and command options follow those linked references; target baseline is Ubuntu 24.04 LTS, Fedora 44, or RHEL 9, with other versions requiring explicit verification. No SSH target, package installation, systemd change, or Ansible runtime was executed while authoring.
