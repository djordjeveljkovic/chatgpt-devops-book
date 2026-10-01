# Chapter 78 continuation

Status: complete

## Written material
Role interface/layout; complete defaults/tasks/template/playbook; Vault create and execution; external lookup trust; multi-host rotation/failure; exercises/sources.

## Concepts and terminology
Role versus collection, defaults/interface, Vault at-rest versus runtime secrecy, no_log/diff scope, rotation overlap, controller lookup identity.

## Examples and cross-references
Configuration-only root-owned environment role, limited whitespace-free URL serialization; no implicit runtime deployment. Links 077,107,175.

## Open threads
Independent review; real Ansible/Vault/systemd/SELinux/AppArmor integrations unrun. Example credential fictional.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Official Ansible roles/Vault-encryption/Vault-use/logging docs inspected 2026-10-01. No runtime claims.

Local check: tools/check_book.py --chapters 71-80 checked shell/Python syntax, YAML parsing and links 2026-10-01. Initial079 shorthand CloudFormation tag exceeded generic YAML parser; changed to equivalent Ref mapping, then reran. No runtime/provider semantics claim.
