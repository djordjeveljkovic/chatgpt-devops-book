---
book: The Complete DevOps Engineering Book
volume: 3
volume_title: "Networking and Traffic"
chapter: 26
title: "SSH and Remote Administration"
slug: ssh-and-remote-administration
status: draft
summary: ../../_ai/chapter-summaries/026-ssh-and-remote-administration.md
---

# Chapter 26 — SSH and Remote Administration

## Why this matters

Harbor's team needs to repair a failed DispatchDesk host over a remote connection. A key file, an SSH daemon and an open TCP port are each only part of that path. The client must authenticate the server, the server must authenticate the user, and the operator must know which host and account are receiving each command. A rushed host-key prompt can give an attacker the credentials the connection was meant to protect.

SSH provides an encrypted transport, server identity checking, user authentication and channels for sessions or forwarding. This chapter applies it to ordinary Linux administration after the routing and TLS fundamentals in [Chapter 21](021-packets-addresses-and-routing.md) and [Chapter 25](025-tls-certificates-and-trust.md). The examples use placeholders and do not connect to a real system.

## Keys, agents and host verification

An SSH key pair has a private key that the client protects and a public key that can be installed for an account. The private key should remain under the owner's control, be protected by file permissions and preferably an encrypted passphrase. A passphrase protects a stolen file at rest; it does not make a compromised, unlocked account safe. Hardware-backed keys and short-lived certificates can improve controls when the organization supports them.

On Ubuntu, the client is provided by `openssh-client` and the server by `openssh-server`. Fedora uses the `openssh-clients` and `openssh-server` packages; RHEL requires enabled repositories and an entitled system where applicable. Package names, service state and host policies should be checked for the exact release. Installing a server package does not mean it should be exposed to untrusted networks.

To create a dedicated, encrypted Ed25519 user key, run as the account that will initiate SSH. `-f` names a new file in the user's SSH directory; choose a distinct filename and enter a strong passphrase when prompted. This command creates private and public key files locally. It does not install the public key anywhere or authorize access by itself:

```bash
ssh-keygen -t ed25519 -a 64 -f "$HOME/.ssh/dispatchdesk_ops"
```

The `-a` value controls key derivation work used to protect the private key with its passphrase. Availability and exact algorithms depend on the installed OpenSSH release and policy. Back up the private key only through the approved secret-protection process; never paste it into chat or a server ticket. Protect `~/.ssh` and private key permissions so OpenSSH accepts them.

The public key is not secret, but installing it grants an authentication capability. An administrator can place it in the intended account's `~/.ssh/authorized_keys` through an approved provisioning path. Confirm the account, host, allowed commands and key retirement plan. A shared, long-lived administrator key makes attribution and revocation harder.

An SSH client also authenticates the server using its host key. On first connection, obtain the expected host-key fingerprint through an independent trusted channel, such as the provider console or controlled configuration system, and compare it with the fingerprint shown by the client. Accepting an unknown fingerprint based only on the same network path the SSH connection uses does not authenticate that path. `ssh-keyscan` can collect keys but does not establish their authenticity. Rotate known host keys through a documented process and alert on unexpected changes.

An agent can hold decrypted keys in memory to avoid repeated passphrase entry. Add only keys needed for a task and use a bounded lifetime where supported. Forwarding an agent to a remote host lets processes on that host request signatures from the local agent; it does not copy the private key, but it expands the trust boundary. Avoid agent forwarding unless you understand and need that remote capability. [OpenSSH manual index](https://www.openssh.com/manual.html).

## Bastions, tunnels and connection reuse

A bastion host is an explicitly managed entry point to otherwise private hosts. `ProxyJump` lets the client open a channel through it while still negotiating the target SSH session with the destination host. The target's host key must still be verified independently. A bastion reduces exposed paths only when network policy, account controls, logging and patching support that role.

A host-specific client configuration can keep connection choices visible. Save the following in `~/.ssh/config` after replacing each placeholder with the approved account, host name, key path and bastion. This example avoids forwarding the local agent and requires the client to reject an unknown host key:

```sshconfig
Host dispatchdesk-prod
    HostName api-prod.example.internal
    User ops
    IdentityFile ~/.ssh/dispatchdesk_ops
    IdentitiesOnly yes
    ProxyJump ops@bastion.example.net
    ForwardAgent no
    StrictHostKeyChecking yes
    ConnectTimeout 10
```

Before the fingerprint has been installed through your verified enrollment process, `StrictHostKeyChecking yes` will fail closed. Do not change it to `no` merely to make the first connection work. `IdentitiesOnly yes` limits which configured identity is offered for this host; `ConnectTimeout` bounds connection establishment, not the duration of a remote command. OpenSSH uses the first obtained value for each option, so keep more-specific host rules before general defaults. [SSH client configuration manual](https://man.openbsd.org/ssh_config).

Inspect the effective settings without connecting:

```bash
ssh -G dispatchdesk-prod
```

The expanded output can contain usernames, paths and hostnames; treat it as operational information. Once host identity has been independently established and the expected key has been enrolled, `ssh dispatchdesk-prod` uses the named profile. Check the remote hostname and account immediately after login before running a command that changes state.

A local forward can make a private database reachable through an approved bastion without binding a public listener on the operator's laptop:

```bash
ssh -N -L 127.0.0.1:15432:db.internal.example:5432 ops@bastion.example.net
```

`-N` requests no remote shell, and `-L` listens only on local loopback port 15432, forwarding through the SSH connection to port 5432 as resolved from the bastion's network. Keep the session open while using a client against `127.0.0.1:15432`; stop it with Ctrl-C. The database still authenticates and authorizes the client. A tunnel does not bypass the database's security contract. Do not bind to `0.0.0.0` unless sharing that local port is explicitly intended and protected.

Connection multiplexing can reuse one authenticated TCP transport for later sessions, reducing repeated handshake cost. It also means closing one terminal may leave a control socket and transport active. If enabled, use a private control-socket path with appropriate permissions and a bounded `ControlPersist`. Avoid a world-writable socket directory or broad multiplexing across unrelated accounts. Multiplexing changes lifecycle and audit expectations, not the identity of the remote target.

## A reliable remote maintenance session

Before a production change, confirm the incident owner, host identity, target account, change window, recovery console and rollback command. Capture current service state and the exact configuration being changed. Keep an independent session or console path where feasible; a network change can sever the only connection used to recover it.

A bounded remote command can carry an explicit timeout and avoid allocating an interactive pseudo-terminal unless the command requires one:

```bash
ssh -T dispatchdesk-prod 'sudo -n systemctl status dispatchdesk-api.service --no-pager'
```

`-T` disables pseudo-terminal allocation. `sudo -n` fails instead of prompting in an automation session. The command is observational, but `systemctl status` may return a nonzero status if the service is unhealthy; preserve both output and exit code. Shell quoting occurs across local and remote command layers, so keep arguments simple or use a controlled script deployed through the normal change process. Avoid pasting an unreviewed multiline shell command into a privileged session.

For a planned configuration update, first verify the new file against the service's parser, install it atomically with correct ownership, then reload or restart according to the service's supported behavior. Observe the unit and application health afterward. Keep the old configuration until the new behavior is proven, then remove obsolete credentials and temporary access according to policy. SSH command completion does not prove an asynchronous deployment completed successfully; inspect the target's resulting state.

## Recover a failed SSH change

An operator installs a replacement key but overwrites the only working `authorized_keys` entry with a malformed line. Before ending the current session, open a second connection using the new key and confirm the server accepts it. If it fails, keep the original session open and restore the known-good file with correct owner and permissions. If all sessions are lost, use the provider console or documented out-of-band recovery path; do not weaken host-key verification to compensate for a user-key failure.

For an unexpected host-key warning, stop and verify whether the host was rebuilt, the DNS name now points elsewhere, a bastion is being reused, or an active interception is possible. Compare the fingerprint against an independent record. Update the known-host entry only after identity and change authorization are established. Deleting the old key without checking removes the evidence but does not authenticate the new host.

If SSH times out, determine whether name lookup, route selection, TCP connection, key exchange, user authentication or the remote command stalled. `ssh -vv` can help locate the client stage, but verbose logs expose host and account details. Combine it with server logs through the provider console and inspect firewall policy from [Chapter 27](027-firewalls-and-network-policy.md). Changing `sshd` settings without validating syntax or preserving a working session can lock out every operator.

## Exercises, review questions and takeaways

1. Create a dedicated key in a disposable user account and inspect its public fingerprint. Guidance: the public key can be inspected; protect the private key and do not install either key on a production system for practice.
2. Compare the SSH host-key fingerprint with a value obtained from an independent console. Guidance: the independent channel is what gives the comparison meaning.
3. Draw the client, bastion and private database tunnel. Guidance: distinguish the SSH target's verified host key from the database's own credentials and authorization.
4. Plan a safe `authorized_keys` rotation. Guidance: add, test a second independent session, then remove the old key while retaining a recovery route.

Review questions: What does the agent expose when forwarded? Why does `ssh-keyscan` not authenticate a host? Which SSH phase has `ConnectTimeout` bounded? Good answers separate key storage, server identity, user identity and command execution.

Verify both host and user identities before changing a remote system, and keep a recovery path for each access change. Continue to [Chapter 27](027-firewalls-and-network-policy.md) to change packet policy without losing that path.
