---
book: The Complete DevOps Engineering Book
volume: 3
volume_title: "Networking and Traffic"
chapter: 25
title: "TLS, Certificates and Trust"
slug: tls-certificates-and-trust
status: complete
summary: ../../_ai/chapter-summaries/025-tls-certificates-and-trust.md
---

# Chapter 25 — TLS, Certificates and Trust

## Why this matters

A DispatchDesk user sees a certificate warning after Harbor renews its public certificate. The web server process is running and TCP port 443 accepts connections, but the browser cannot establish the identity and protected channel it expects. A port check cannot confirm a certificate chain, hostname or handshake. The team needs evidence from the TLS endpoint that the user actually reached.

This chapter explains the identity checks below the HTTP request from [Chapter 24](024-http-and-api-traffic.md). Examples use OpenSSL against a hostname you control or are authorized to inspect. Certificate validation is security-critical: a diagnostic that disables verification can help isolate a cause briefly, but it never repairs trust.

## Certificate chains and names

TLS begins with a handshake in which client and server negotiate protocol parameters, prove possession of key material and derive traffic keys. In a typical web connection, the server presents an end-entity certificate and often intermediate certificates. The client validates the chain to a trust anchor in its configured store. The certificate's subject alternative names (SANs) must cover the hostname the client intended to reach. A valid signature by itself does not establish that the certificate belongs to the requested service. [TLS 1.3 specification](https://www.rfc-editor.org/rfc/rfc8446.html) and [X.509 PKI profile](https://www.rfc-editor.org/rfc/rfc5280.html).

The server normally sends the leaf and required intermediate certificates; it should not need to send the root trust anchor. A browser's cache can hide a missing intermediate that breaks a clean client. Test from an environment that has not already learned the chain, and inspect the certificates actually presented on the wire. Corporate TLS inspection or a private CA can alter the trust chain seen by a managed client; document that boundary rather than treating every certificate as a public-Web PKI chain.

The client sends Server Name Indication (SNI) during a TLS handshake so a shared endpoint can select a certificate for the intended DNS name. The HTTP `Host` header comes later for HTTP/1.1; changing it alone does not change the SNI used in the handshake. A request to an IP address can therefore see a default certificate even if an HTTP header names a virtual host. Certificate hostname validation remains against the intended service name.

TLS protects confidentiality and integrity for a connection and authenticates the peer according to the configured trust checks. It does not guarantee the peer is the correct application after a trusted proxy terminates TLS, nor does it make application data safe to log. Mutual TLS adds client certificate authentication when the application and policy require it. A client certificate is identity material with a lifecycle, not a replacement for authorization inside the service.

## Issuance, renewal and termination

A certificate lifecycle begins with an identity and issuance policy: which names are permitted, which authority signs, how challenges prove control, where private keys live, and who can request or deploy a replacement. ACME automates issuance and renewal through domain-control challenges. HTTP-based validation requires the challenge response to be reachable through the service path; DNS-based validation requires a TXT record to be provisioned for the name, commonly through a DNS provider API when fully automated. The right method depends on reachability, wildcard needs and control of the DNS API, and each CA defines its own supported policy. Private key files should be readable only by the service identity that needs them. [ACME standard](https://www.rfc-editor.org/rfc/rfc8555.html) and [Let's Encrypt challenge types](https://letsencrypt.org/docs/challenge-types/).

Renewal is a deploy operation as well as a certificate request. A new file on disk does not prove that a long-running server loaded it. Verify file permissions, chain completeness, names, expiration and the service's reload behavior. Where supported, reload after a successful replacement and test a fresh handshake. Keep the previous known-good key and certificate briefly under the organization's policy so rollback is possible, then remove retired secrets securely according to retention rules.

For a reverse proxy, the public TLS endpoint may be separate from the application. Renewing the app's internal certificate does not change the proxy's certificate. Monitoring should check both remaining validity and successful external validation through the same SNI name clients use. Alert with enough time to repair a failed renewal, while avoiding a noisy daily expiry alert that responders learn to ignore.

A single hostname can be served by several load balancer nodes or regions. Deploy the renewed chain consistently and probe every serving endpoint, including nodes reached by address overrides or regional routing. One node retaining an expired certificate can create intermittent failures that resemble a client-side cache problem. Keep issuance and deployment idempotent so a retry after a partial rollout converges safely.

TLS versions and cryptographic algorithms also have compatibility policy. Do not copy an old cipher-list workaround from a client error without first identifying the peers and negotiated protocol. Compare a successful and failing client's negotiated version, signature algorithms, trust store and requested SNI. A server can present the expected certificate yet fail before HTTP because no mutually supported parameters remain. Fix the supported configuration at the owned TLS endpoint and verify with representative clients; do not lower protocol policy globally to make one obsolete client pass without an explicit risk decision.

## Diagnose TLS with openssl

Run the following from a Linux client that has OpenSSL installed. Use a real hostname you are authorized to inspect, and substitute it for `api.example.com`. The command opens a TLS connection to the hostname on port 443, sends SNI, requests certificate verification, prints the chain and negotiated session, then closes stdin so `s_client` can finish without an interactive HTTP exchange:

```bash
openssl s_client \
  -connect api.example.com:443 \
  -servername api.example.com \
  -verify 5 \
  -verify_hostname api.example.com \
  -verify_return_error \
  -showcerts </dev/null
```

`-connect` selects the network endpoint; `-servername` supplies SNI; `-verify 5` enables peer certificate verification with a maximum chain depth of five, and `-verify_hostname` checks the intended DNS name; `-verify_return_error` makes verification errors fail the diagnostic rather than continuing as though trust succeeded; `-showcerts` displays the certificates sent by the server. `</dev/null` provides end-of-input so the client does not wait for terminal input. The full output can include certificate details and infrastructure names; share it according to your security policy. OpenSSL command behavior can vary by release, so consult the installed `s_client` manual. [OpenSSL s_client manual](https://docs.openssl.org/3.5/man1/openssl-s_client/).

When a service uses a non-default port, change the port in `-connect` while preserving the DNS hostname in both SNI and hostname verification. To test a specific approved IP without changing DNS, set `-connect` to that IP and leave `-servername` and `-verify_hostname` set to the intended name. This separates address selection from TLS identity. Do not replace the name with the IP unless the certificate actually contains the required IP address identity.

A successful TLS handshake does not prove HTTP routing or application health. After verification succeeds, use curl with the same URL hostname and, where needed, a controlled address override as described in Chapter 24. Compare the TLS endpoint's certificate with the HTTP response and reverse-proxy logs.

## Recover a certificate failure

Harbor's proxy presents a certificate that expired yesterday. First record the client name, resolved IP, time, certificate issuer, SANs, validity interval and verification error. Ask whether all clients fail or only clients using one resolver, geography, proxy or trust store. A mismatched SAN points toward the wrong virtual-host certificate or hostname; an expired leaf suggests renewal or deployment; an incomplete chain often differs between cached and clean clients.

Inspect the proxy's configured certificate paths and the renewed files without printing private key contents. Check certificate expiry and names with OpenSSL, validate the chain against the intended trust roots, and confirm the running service loaded the files. For example, `openssl x509 -in server.crt -noout -subject -issuer -dates -ext subjectAltName` prints selected public certificate fields. It does not verify the network endpoint or prove the private key matches. Validate those as separate checks using the service's supported tooling.

If renewal failed, restore availability using the organization's known-good certificate and key pair or complete the approved renewal path. Do not ask users to ignore warnings, turn off hostname checks, or download a replacement key from an unverified channel. Test a new connection from an independent client, then verify HTTP routing and application health. Investigate why monitoring failed to provide enough repair time.

## Exercises, review questions and takeaways

1. Connect to a hostname with `-servername` set, then test an approved IP while preserving hostname verification. Guidance: the IP changes the network destination; SNI and SAN checking continue to use the intended name.
2. Explain why one browser succeeds while a clean client reports an incomplete chain. Guidance: cached intermediates can conceal a server's missing certificate-chain element.
3. Design a certificate renewal check. Guidance: observe both remaining lifetime and a fresh externally verified handshake after deployment.
4. A TLS handshake succeeds but the API returns `404`. Guidance: TLS established a protected connection to an endpoint; inspect HTTP host routing and the serving hop next.

Review questions: What does a certificate chain establish? Why are SNI and the HTTP `Host` header different? When is disabling verification unsafe? Good answers identify the identity, validation and routing stages separately.

Test the peer name and chain that clients actually trust, then verify the HTTP behavior through the same endpoint. Continue to [Chapter 26](026-ssh-and-remote-administration.md) for authenticated remote administration over a separate encrypted protocol.
