---
book: The Complete DevOps Engineering Book
volume: 10
volume_title: "AWS Production Services"
chapter: 99
title: "CloudFront and Edge Delivery"
slug: cloudfront-and-edge-delivery
status: complete
summary: ../../_ai/chapter-summaries/099-cloudfront-and-edge-delivery.md
---

# Chapter 99 — CloudFront and Edge Delivery

## Origins, caching and invalidation

Amazon CloudFront is a content delivery network with distributions, cache behaviors and origins. A viewer request matches a behavior, CloudFront evaluates its cache policy, and the request either uses a cached object or reaches an origin. The origin may be an S3 bucket for static files or an HTTP service such as an ALB-backed application. Edge caching can reduce latency and origin work, but it introduces another layer of cache-key and freshness behavior that must be designed intentionally.

The cache key determines which requests can share a response. By default, the distribution domain and URL path identify an object. A cache policy can include selected query strings, headers and cookies. If the origin varies a response by `Accept-Language` but that header is absent from the cache key, one language's response can be served to another request. If irrelevant tracking query strings are included, the cache stores duplicate copies and reduces the hit ratio. Include every request value that changes the representation, and avoid values that do not. AWS explains [CloudFront cache keys](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-the-cache-key.html) and [cache policy settings](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cache-key-understand-cache-policy.html).

TTL is a correctness and origin-capacity decision. CloudFront cache-policy minimum, default and maximum TTL interact with origin `Cache-Control` and `Expires` headers. A positive minimum TTL can keep an object cached even when the origin asks for immediate expiry or revalidation; choose it only when serving that staleness is safe. Static assets with content-hashed filenames can use long TTLs because changed content receives a new URL. Mutable HTML and API responses usually need short TTLs or no shared caching unless a deliberate freshness contract exists. Origin `Cache-Control: private` or `no-store` should not be bypassed casually with an incompatible policy. See [managed cache policy behavior](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html).

Invalidation removes selected cached objects, but it does not update an origin or fix a wrong cache key. A release that overwrites `/app.js` may leave old bytes at the edge and in browsers; publishing `/app.7f3a…js` gives each version a distinct path, while a short-lived HTML entry point references the current asset. Use invalidation for urgent correction or mutable paths after a reviewed deployment. Broad invalidations may have cost and operational implications; inspect current AWS terms before relying on assumptions about free quantities or propagation timing. Do not use invalidation as a substitute for versioned deployment and explicit cache headers.

## Headers, authorization and dynamic content

Separate three decisions: what CloudFront caches, what it forwards to the origin, and what it sends to the viewer. A cache policy controls key dimensions and TTL. An origin request policy can forward additional headers, cookies or query strings without including all of them in the key. A response headers policy can add CORS or security headers on both cached and origin responses. These are separate controls. Forwarding `Authorization` to an origin does not automatically make a response safe to share among viewers; if authorization affects the result, disable shared caching or include a carefully designed identity dimension and prove isolation. Avoid putting raw tokens or session cookies in a broad cache key.

For a private S3 origin, Origin Access Control (OAC) lets CloudFront make authenticated origin requests so the bucket does not need public read access. OAC protects the origin path; it does not decide which viewers are authorized to receive a cached object. Viewer restrictions can use signed URLs or signed cookies with expiry and optional IP conditions, or the application can authorize a dynamic response. For S3-backed private content, restrict direct bucket access as well as CloudFront viewer access. AWS recommends [OAC for S3 origins](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html) and documents [viewer access controls](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-overview.html).

CORS is also representation-sensitive. If origin responses vary by `Origin`, include the relevant header in the cache key or configure a safe fixed policy. A response headers policy can add CORS headers, but viewer response headers do not change how CloudFront cached the object. Do not pair `Access-Control-Allow-Origin: *` with credentialed browser requests. Review the browser's preflight and actual response separately, and test both cached and miss paths. CloudFront's [response headers policy guide](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/modifying-response-headers.html) describes header changes.

Use separate behaviors for materially different content classes: immutable static assets, short-lived public catalog data, authenticated application endpoints and private downloads. Set allowed HTTP methods and origin forwarding deliberately. If an API sends personalized order data, a shared cache with a key that omits identity could expose one customer's response to another. `Cache-Control: private` is a useful signal, but validate the CloudFront policy as configured. Review policy changes as access-control changes, not just performance tuning.

## Reducing origin load without stale-data surprises

Suppose DispatchDesk serves a public restaurant menu through CloudFront. A release changes a menu price, but customers continue seeing the old price from an edge cache. The failure was not necessarily a stale origin; it may be a long TTL, a cache key shared across a locale or an HTML page that references an old asset. Compare the viewer request path and headers, `Age`/cache status, origin response headers, distribution behavior and deployment asset version. Test a request with a cache-busting path in a controlled way, then correct the policy or publish a new version. Do not invalidate every object until the affected key and intended freshness are understood.

For an API request that returns customer-specific order status, default to no shared caching unless the endpoint has a designed cache contract. For a public restaurant listing, cache by path and perhaps a bounded locale dimension; avoid arbitrary query parameters that do not affect the representation. A useful decision record names the source of truth, acceptable staleness, cache-key dimensions, TTL, invalidation owner and incident response. If an origin outage occurs, decide in advance whether stale public content may be served. Stale order or authorization state should not be treated as equivalent.

Observe the whole path. CloudFront standard or real-time logs can help investigate request-level behavior, while CloudWatch metrics summarize requests, bytes, errors and cache efficiency. `CacheHitRate` is an additional metric that must be enabled and can add charges; verify current pricing and availability before using it. Compare it and origin load with application latency, origin error rate and deployment events. A higher hit ratio is not success if users receive incorrect data. Track a small set of bounded dimensions and use request IDs in logs where available; avoid high-cardinality metric labels derived from full URLs or customer IDs. Consider regional origin pressure, not only edge metrics: a cache miss storm can expose an undersized origin.

A read-only investigation can use the distribution console or an authorized API inventory, but distribution configuration often contains hostnames, policy identifiers and account topology. Restrict saved output. For browser evidence, request the same object twice and compare status, `Age`, cache-status headers if configured, `Cache-Control`, `Vary` and response body hash. Use a test object, not a customer record. A response that says “hit” only proves reuse under the current key; it does not prove the key includes all required identity and locale dimensions.

During a release, publish immutable assets first, then update the HTML or manifest pointer, verify the new version through the distribution, and keep the previous assets available for clients with cached HTML. If a rollback is needed, restore the old pointer or deploy a new manifest. For API freshness corrections, update origin behavior and use targeted invalidation if required. Confirm from multiple request contexts and regions as appropriate; an origin-only check does not establish edge behavior. Keep the rollback procedure safe if edge propagation is not instantaneous.

## Exercises and answer guidance

1. A response varies by `Accept-Language`, but CloudFront's cache key contains only the path. What can happen? Requests can share the wrong language response; include the relevant bounded header in the key or make the response invariant.
2. An origin returns `Cache-Control: no-store`, but a positive minimum TTL is configured. Is the object necessarily uncached? No. CloudFront's minimum TTL can override origin directives; set a policy consistent with the required freshness and privacy.
3. S3 objects are private, and OAC is enabled. Does that authorize every viewer? No. OAC protects CloudFront-to-S3 access; viewer authorization still needs a signed URL/cookie or application policy.
4. The hit ratio improves after including all query strings, but origin requests remain high. What should be checked? Determine whether irrelevant query values fragment the key and whether each dimension actually changes the representation.

Review questions: which responses are shareable, what request values define representation, what is the maximum safe staleness, who can access the origin directly, and which evidence confirms both cache behavior and user-visible correctness?

## Verification and primary sources

AWS CloudFront cache keys/policies, private content, OAC, response headers and managed policy documentation was inspected on 2026-10-04. No distribution, origin, bucket policy, cache behavior, invalidation, signed URL, viewer request or customer content was created or changed. Static reasoning does not prove policy behavior, cache propagation, edge latency, origin capacity or privacy correctness in a live distribution.

Primary references: [cache keys](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-the-cache-key.html), [cache policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cache-key-understand-cache-policy.html), [managed cache policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html), [private content](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-overview.html), [S3 OAC](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html), [response headers policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/modifying-response-headers.html), and [CloudFront metrics](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/programming-cloudwatch-metrics.html).
