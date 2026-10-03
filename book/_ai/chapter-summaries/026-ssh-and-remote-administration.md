# Chapter 26 continuation

Status: draft

## Written material
SSH transport and identities; key creation and permissions; independent server host-key validation; bounded agent use; host-specific client configuration and bastion; local tunnel; session and remote change practice; key rotation and failure recovery; exercises.

## Exact next section
Independent technical and editorial review.

## Concepts and terminology
Private/public key, passphrase, host key, known_hosts, agent, agent forwarding, ProxyJump, local TCP forwarding, SSH control master, recovery console.

## Examples and cross-references
All hosts and identities are placeholders. SSH config example uses strict host checking and disables agent forwarding. Database tunnel listens only on local loopback. Remote systemd query is observational. Links to Chapters 21, 25 and 27.

## Open threads
Independent review; no host connection, key creation, forwarding or server configuration executed. Package names and options vary by distribution/OpenSSH release.

## Verification
Inspected OpenSSH manual index and current OpenBSD `ssh_config` manual on 2026-10-02. Installed client reports OpenSSH 10.5p1. Parsed the chapter's exact sample with read-only `ssh -F /tmp/book-ssh-config -G dispatchdesk-prod`; output reflected the host, user, identity, bastion, no agent forwarding, strict host checking and timeout. The global `/etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf` cannot be used because its permissions are rejected by OpenSSH. No network connection was made.
