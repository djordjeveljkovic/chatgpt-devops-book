# Chapter 55 continuation

Status: complete; independently reviewed and approved.

## Written material
Bridge, host and none driver boundaries; user-defined service DNS; port publication and exposure; cross-container connectivity lab; failure localization; exercises and answers, takeaways and navigation.

## Concepts and terminology
User-defined bridge, default bridge, container DNS, host networking, published port, host firewall, daemon host/context.

## Examples and cross-references
Named Nginx service and ephemeral BusyBox client on a user-defined bridge; no host port. Correct command continuation and inspection after service creation. Links to chapters 27, 52 and 56.

## Open threads
No unresolved review findings. Engine pre-28 localhost publishing caveat, host firewall and rootless/Desktop behavior remain version/platform sensitive. No runtime network test.

## Exact next section
None. Continue with Chapter 57.

## Verification
Official Docker bridge, host, port publishing, firewall and network CLI docs inspected 2026-10-03. Independent reviewer `review_055` approved SHA256 `7fcd0eebe70ab7b3831c1d5361db48171335c643642ce83e409855a0a9f4cf19`; six shell blocks and local links passed. Docker commands were not run.
