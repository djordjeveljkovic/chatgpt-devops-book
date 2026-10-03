# Chapter 25 continuation

Status: complete

## Written material
TLS handshake and trust; certificate chains, SAN names, SNI, mutual TLS; issuance and renewal/deployment; OpenSSL `s_client` and certificate inspection; expired/wrong-chain diagnosis; rollback and compatibility investigation; exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
TLS handshake, trust anchor, end-entity/intermediate certificate, SAN, SNI, hostname verification, client authentication, renewal/deployment, protocol compatibility.

## Examples and cross-references
OpenSSL s_client tests chosen address with intended SNI and hostname. Example uses replaceable `api.example.com`. Certificate inspection is read-only. Links to Chapters 24 and 26.

## Open threads
Independent review found no material issue. An optional bounded-execution improvement remains: wrap `openssl s_client` with GNU `timeout` and document its exit behavior. No public endpoint was contacted and no certificate was deployed.

## Verification
Inspected RFC 8446, RFC 5280 and OpenSSL 3.5 `s_client` documentation on 2026-10-02. The installed OpenSSL is 3.6.4; `s_client -help` confirmed `-verify`, `-showcerts`, `-servername`, `-verify_hostname` and `-verify_return_error` options. Command checks confirmed these options are available; no handshake with an external hostname was attempted.
