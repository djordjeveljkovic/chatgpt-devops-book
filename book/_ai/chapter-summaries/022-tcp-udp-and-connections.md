# Chapter 22 continuation

Status: complete

## Written material
TCP/UDP endpoint distinctions; handshakes, stream framing, retries and backpressure; timeout stages; Linux socket states; focused `ss` use; complete bounded loopback TCP/UDP exchange; controlled tcpdump example; connection-failure recovery; exercises and review questions.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Transport endpoint, ephemeral port, stream framing, datagram, retransmission, socket state, connect/read/overall deadline, listener queue, packet observation point.

## Examples and cross-references
Python 3.14 lab binds only to IPv4 loopback port 18080, exchanges one newline-framed TCP message or one UDP datagram, has bounded socket waits, and makes no persistent changes. Links to Chapters 20, 21, 23, 28, 161 and 162.

## Open threads
No material review findings. Packet capture command was not run; no remote firewall, congestion, IPv6 dual-stack or application database was tested.

## Verification
Inspected RFC 9293, RFC 768, Linux TCP/UDP and `ss` manuals, Python socket documentation and upstream tcpdump manual on 2026-10-02. Executed exact TCP and UDP examples outside sandbox on Python 3.14.7: both exchanges passed; stopped-server cases produced `ConnectionRefusedError` and `TimeoutError` as described; `ss` showed the loopback listener. Exercised the TCP line reader with writes split across a socketpair and confirmed framing. Server processes exited and released their sockets. No production socket or firewall settings changed.
