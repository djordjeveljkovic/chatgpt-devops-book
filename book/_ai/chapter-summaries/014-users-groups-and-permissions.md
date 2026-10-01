# Chapter 14 continuation

Status: complete

## Written material
Complete chapter: numeric credentials and group refresh; file versus directory modes; umask and immutable releases/mutable state; ACL mask/inheritance; scoped sudo and redirection; Ubuntu AppArmor and Fedora/RHEL SELinux; state-directory permission incident; exercises and guidance.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
UID/GID, supplementary groups, directory search, ACL mask/default ACL, umask, mandatory policy, runtime/deployment identity separation.

## Examples and cross-references
Inline id, mode-change and subshell umask labs. Chapters 10/15/16 referenced; final link Chapter 15. Fictional state migration requires stopped writers and database-safe handling, no actual migration claimed.

## Open threads
Independent review pending. No multiuser/ACL/sudo/SELinux/AppArmor operational testing. Fedora quick docs fetch denied; official Fedora QA enforcement test and current basic release criteria inspected as fallback.

## Verification
Inspected Linux pathname resolution/ACL and GNU chmod manuals, Ubuntu AppArmor, RHEL9 SELinux guide, upstream sudoers hosted man7 (sudo.ws robots denied). Fedora direct quick documentation and raw mirror access failed; official QA SELinux test and basic release criteria subsequently inspected. Executed all three Bash blocks together in a temporary directory under ordinary UID1001: id context; private directory700/file600 then400; creation file640/directory750 under umask027. Directory context cleaned. Previously inspected Bash5.3.20/coreutils9.11; this is local syntax/behavior evidence, not baseline image validation.
