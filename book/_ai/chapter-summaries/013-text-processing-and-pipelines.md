# Chapter 13 continuation

Status: complete

## Written material
Complete bespoke chapter on descriptors, ordered redirection, pipe backpressure/SIGPIPE, Bash pipeline statuses, literal search, delimited awk aggregation, sorted frequencies, JSON Lines/jq, and a failed-collector incident. Includes four exercises with guidance and sources.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Standard input/output/error; pipe backpressure; PIPESTATUS; pipefail; record/schema contract; counting unit; JSON Lines; slurp memory tradeoff.

## Examples and cross-references
Disposable redirection fixture; failed producer with successful wc; tab-separated notification aggregation; sorted outcomes; jq order selection/count. Links Chapters 7, 14; discusses Chapters 11, 17, 18. DispatchDesk notification semantics retained.

## Open threads
Independent review pending. Real collectors, distributions, log rotation and permissions incident are explanatory scenarios, not executed integrations.

## Verification
Inspected upstream Bash manual hosted man7, POSIX awk manual, GNU sort manual and official jq 1.8 manual; GNU Bash website fetch timed out. Executed every Bash block sequentially in a Python-managed temporary directory, cleaned on exit: stdout/stderr separation; pipeline statuses 0/1 and stages 1 0; retries=2 mean_ms=160.0; outcome frequencies retry2/sent1; JSON order-2/order-4 and count2. Local jq1.8.2, previously inspected Bash5.3.20/coreutils9.11; not baseline distribution validation. No infrastructure execution.
