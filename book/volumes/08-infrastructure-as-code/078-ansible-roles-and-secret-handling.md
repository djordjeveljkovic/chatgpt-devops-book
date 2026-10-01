---
book: The Complete DevOps Engineering Book
volume: 8
volume_title: "Infrastructure as Code"
chapter: 78
title: "Ansible Roles and Secret Handling"
slug: ansible-roles-and-secret-handling
status: complete
summary: ../../_ai/chapter-summaries/078-ansible-roles-and-secret-handling.md
---

# Chapter 78 — Ansible Roles and Secret Handling

## Reusable roles and collections

Harbor's host configuration now needs an application environment file on several machines. Copying the same tasks between playbooks would make a later permission correction easy to miss. A role packages the tasks, defaults, templates, and handlers that implement one contract. A collection packages a broader namespace of roles, plugins, and modules for distribution. Reuse helps when it preserves an owned interface; it hurts when a dependency silently changes host policy.

Before this chapter, read [inventory and playbooks](077-ansible-inventory-and-playbooks.md). The example here installs a restricted environment file only. It does not deploy an application, start a database, or assume that a service automatically reads the file. A real DispatchDesk systemd unit must explicitly name its EnvironmentFile, and the application must implement the documented configuration names. Keeping that boundary visible prevents “configuration installed” from becoming an unearned claim that orders work.

Use defaults for caller-overridable policy choices such as a configuration directory. Use task validation for invariants, such as a required database reference and valid log level. Do not hide secrets in high-precedence role variables where callers cannot easily replace them. Prefix role variables to reduce accidental collisions. A shared role's variables, output facts, notifications, and file ownership form its interface.

Create the following controller-side layout:

```text
site.yml
inventory.ini
secrets.yml
roles/
  dispatchdesk_config/
    defaults/main.yml
    tasks/main.yml
    templates/environment.j2
```

The inventory is the explicit disposable-host inventory from Chapter 077, with reachable approved addresses. Each complete role file appears below. `roles/dispatchdesk_config/defaults/main.yml`:

```yaml
dispatchdesk_config_directory: /etc/dispatchdesk
dispatchdesk_log_level: INFO
dispatchdesk_port: 8080
```

`roles/dispatchdesk_config/templates/environment.j2`:

```ini
PORT={{ dispatchdesk_port }}
LOG_LEVEL={{ dispatchdesk_log_level }}
DATABASE_URL={{ dispatchdesk_database_url }}
```

This template is valid only for single-line values whose characters are suitable for the stated systemd environment-file syntax. The role rejects whitespace and newline characters in the URL to keep the small example's assumption explicit. Complex credentials should use a documented secret-file or credential-loading mechanism, rather than inventing ad hoc quoting that silently changes the password. Do not source this file as arbitrary shell code.

`roles/dispatchdesk_config/tasks/main.yml`:

```yaml
- name: Require a database reference
  ansible.builtin.assert:
    that:
      - dispatchdesk_database_url is defined
    fail_msg: Supply dispatchdesk_database_url through an approved secret source.

- name: Validate nonsensitive configuration choices
  ansible.builtin.assert:
    that:
      - dispatchdesk_log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']
      - dispatchdesk_port | int >= 1024
      - dispatchdesk_port | int <= 65535
    fail_msg: Invalid log level or unprivileged service port.

- name: Validate the limited URL serialization contract
  ansible.builtin.assert:
    that:
      - dispatchdesk_database_url | length > 0
      - dispatchdesk_database_url is not search('\s')
    fail_msg: Database URL must be nonempty and contain no whitespace.
  no_log: true

- name: Create the restricted configuration directory
  ansible.builtin.file:
    path: '{{ dispatchdesk_config_directory }}'
    state: directory
    owner: root
    group: root
    mode: '0700'

- name: Publish the restricted environment file
  ansible.builtin.template:
    src: environment.j2
    dest: '{{ dispatchdesk_config_directory }}/environment'
    owner: root
    group: root
    mode: '0600'
  no_log: true
  diff: false
```

The first validation identifies a missing input without printing it. The secret-bearing validation and template tasks suppress normal task results with `no_log`. `diff: false` avoids rendering the old and new file contents during diff runs. The directory and file are root-only. A system-level systemd manager can read a root-only EnvironmentFile and supply values to a service user; a user-level service has different access requirements and must not be assumed equivalent. A credential delivered into a process environment can still be exposed to that process and privileged inspection tools.

The complete `site.yml` is:

```yaml
- name: Publish DispatchDesk lab configuration
  hosts: lab
  become: true
  gather_facts: true
  serial: 1
  vars_files:
    - secrets.yml
  roles:
    - dispatchdesk_config
```

This is a configuration-only role. It deliberately does not restart an unknown service. If a service deployment role owns the unit and its reading contract, connect file changes to its documented restart/reload behavior and application checks. Avoid a role that restarts everything matching a name pattern because it cannot identify the actual owner.

## Vault and external secret references

Ansible Vault encrypts stored content so the repository can contain encrypted variables or files. At execution time the controller decrypts them with supplied vault credentials. Encryption at rest does not prevent the clear value from existing in memory, reaching the target, or being exposed by an unrelated debug task. [Vault encryption](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_encrypting_content.html) and [using encrypted content](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_using_encrypted_content.html) describe the CLI workflow.

On the controller, as the ordinary user in the playbook directory, create an encrypted variable file:

```bash
ansible-vault create --vault-id lab@prompt secrets.yml
```

`create` opens an editor for a new encrypted file. `--vault-id lab@prompt` labels the vault identity `lab` and prompts for its password. Enter a fictional lab value in the editor, such as:

```yaml
dispatchdesk_database_url: postgresql://lab:example-only@127.0.0.1/dispatchdesk
```

This is example data, not a real database credential. The file written to disk should be Vault-encrypted content, not the clear YAML shown above. Verify its Vault header without decrypting it into a public terminal log. Protect the vault password separately from the repository. Encrypting a file and committing the password beside it defeats the separation.

Run the role with:

```bash
ansible-playbook -i inventory.ini site.yml --syntax-check --vault-id lab@prompt
ansible-playbook -i inventory.ini site.yml --check --vault-id lab@prompt --ask-become-pass
ansible-playbook -i inventory.ini site.yml --limit ubuntu_lab --vault-id lab@prompt --ask-become-pass
```

The syntax check still needs enough variable-loading context to read encrypted content. Check mode predicts supported changes. The final command writes the restricted configuration on the selected disposable host. Repeat for `rpm_lab` only after reviewing the first result. A second unchanged run should report no template modification. Verify file existence, ownership, and permissions on the target without printing its content.

An external secret manager can reduce the number of long-lived secrets stored in the repository. Use an explicitly versioned, documented lookup or application-native fetch mechanism with short-lived identity and scoped access. The lookup usually executes on the controller, so its credentials and network access belong to the controller trust boundary. Do not assume a target IAM role automatically authorizes a controller lookup. Secret-manager outage and denied access need a clear failed-deployment outcome; silently substituting an empty string is unsafe.

Choose Vault when a small team's encrypted source workflow and password custody are manageable. Choose an external manager when centralized rotation, auditing, or dynamic credentials justify its operational dependency. A hybrid can keep nonsensitive configuration in source and reference secret identities. [Credential rotation](../18-security-and-software-supply-chains/175-secrets-and-credential-rotation.md) owns the broader lifecycle policy.

## Operating a multi-host deployment

A configuration change across hosts is not automatically atomic. With `serial: 1`, the first host may receive a new database credential while the second retains the old one. Rotation must allow that overlap or the workflow must coordinate a maintenance event. Updating a file before the application reloads it creates another interval. Design compatibility before running automation: create the new credential, allow old and new during transition if supported, publish and reload sequentially, verify, then retire the old credential.

Do not use a healthy loopback endpoint as proof of database authentication unless that endpoint's contract includes the relevant readiness check. A process can answer `/healthz` while a new credential prevents it from accepting orders. [Probes and graceful termination](../11-kubernetes-foundations/107-probes-and-graceful-termination.md) distinguishes liveness from readiness; the same distinction matters on a VPS.

A realistic failure is a template task succeeding while an application continues using its old environment. Environment variables are normally loaded when the process starts; changing the file alone does not update a running process's memory. Diagnose the deployed file metadata, service unit's reading contract, restart timing, and application connection failures. Recovery can restore the previous approved secret version and restart affected hosts, or complete the new rotation if compatible. Never paste the entire environment into the incident chat to prove which version is installed.

Another failure occurs when the controller lacks the correct vault identity. Ansible fails to decrypt before it can safely use the variables. Check the label, password source, and file encryption context; do not decrypt the file permanently as a workaround. Vault password rotation changes who can decrypt stored content. It does not rotate the database credential inside that content. Treat these as separate operations with separate verification.

Ubuntu 24.04, Fedora 44, and RHEL 9 use the same role YAML and file-mode intent. Target security profiles and SELinux labels still need review when a confined process reads a custom path. The role creates no policy exception and does not disable mandatory access control. RHEL repository entitlement matters when installing controller/target prerequisites, not when interpreting a Vault password. Keep distribution package setup separate from secret custody.

Cleanup on disposable hosts removes the named environment file and, if empty and unused, its lab configuration directory. This destroys the local lab secret copy but does not revoke a real credential. A real cleanup must revoke or rotate credentials and consider encrypted source history, backups, controller temporary files, and logs according to policy. For the fictional example, deleting the lab file is sufficient only because no real database exists.

## Exercises and answer guidance

1. Change only LOG_LEVEL and run twice. Expect one file change then convergence; explain why a separate service owner must apply runtime reload/restart behavior.
2. Does `no_log` prevent a later debug task from exposing the variable? No. Each task and logging path must honor the secret boundary; avoid printing secret-bearing structures.
3. The vault password is rekeyed but the database URL remains unchanged. Has database access rotated? No. Encryption custody changed while the application credential stayed the same.

Review questions: What is a role's public interface? Where does an external lookup execute? Why must rotation tolerate overlap? What evidence verifies permissions without revealing secret content?

Reusable configuration succeeds when its interface and secret serialization are explicit, execution identity is scoped, and file publication is connected to a deliberate runtime and credential lifecycle.

## Sources and verification

Official [roles](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html), Vault encryption/usage, and [logging documentation](https://docs.ansible.com/projects/ansible/latest/reference_appendices/logging.html) were inspected 2026-10-01. No Vault encryption, remote template write, credential rotation, or service integration ran during authoring. All credentials shown are fictional example data.
