# Independent review — Chapter 008

Reviewer: write_delivery (independent of write_foundations)
Date: 2026-10-01
Verdict: approved
Reviewed body SHA256: 7873da3e1a43d88788244b40eb2b28dea259297c87cb2510f25c17eb2838fb67

## Substantive inspection
Read complete execution-context model, all shell lab blocks, risky-command discussion and wrong-directory incident. Inspected upstream coreutils id/cp/rm manuals and local Bash help pwd after GNU site timeout. Independently executed all Bash blocks in a temporary context: observed info→debug→restored info and successful exact-file/empty-directory cleanup. Guards preserve intended context.

## Findings
No material findings. Backup scope is limited to content, privilege escalation is not used as a blind repair, and preview limitations are honest. Local lab does not establish remote recovery behavior.

## Validation and limits
Ran tools/check_book.py --chapters 1-10: no errors/warnings; shell/Python syntax, YAML parsing and local-link checks only. Full chapter prose and examples inspected. CLI/source checks above are documentation evidence, not a claim of live service/cloud execution. Local executed labs are identified per chapter. No cloud accounts, privileged host changes or external integrations used.
