# Independent review — Chapter 15

Reviewer: write_delivery
Date: 2026-10-01
Review focus: Owned processes, signals and durable drain
Reviewed body SHA256: 3cd2938ca9f8c887998afb3209a96323af694afa0746bf7731d24a5da00f7abb

## Inspection and findings

Inspected process context, PIDreuse, descriptor lifetime, psfields/states, zombies/reaping, signal disposition and uncatchableKILL/STOP, kill submission versus waitcompletion, ownchild scope and wrapper exec/forwarding. Drain connects readiness/order-intent durability and ambiguous provider outcome without claiming integration. Generic supervisor wrapper scenario does not prescribe default systemd kill scope. No material issue found.

## Verification and limits

Independently executed exact captured-child exercise: TERM accepted and waitstatus143 under Bash5.3.20, no unrelated processes targeted. Linux signal/wait/process references inspected2026-10-01. Real application drain, wrapper or storageD-state incident unrun.

Final check_book11-18 passed 33 shell syntax blocks and global local links after cleanup additions, with no errors or warnings. Local fixtures used temporary directories and no cloud or protected host mutation.

Verdict: approved
