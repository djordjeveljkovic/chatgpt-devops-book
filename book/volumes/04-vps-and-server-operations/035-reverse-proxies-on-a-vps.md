---
book: The Complete DevOps Engineering Book
volume: 4
volume_title: "VPS and Server Operations"
chapter: 35
title: "Reverse Proxies on a VPS"
slug: reverse-proxies-on-a-vps
status: complete
summary: ../../_ai/chapter-summaries/035-reverse-proxies-on-a-vps.md
---

# Chapter 35 — Reverse Proxies on a VPS

## Put one deliberate boundary at the edge

DispatchDesk listens on an unprivileged loopback port under systemd. A reverse proxy accepts public HTTP connections and forwards selected requests to that private service. This lets a host expose a small set of intentional entry points while keeping application processes off public interfaces. The proxy can also terminate TLS, apply request-size limits and route several hostnames, but each capability requires its own configuration and validation.

This chapter uses Nginx on the Harbor VPS. It assumes Chapter 34's DispatchDesk listener is `127.0.0.1:8080`. It does not create the application, issue a certificate or open cloud-provider firewall rules. First verify the app locally; then configure the proxy; finally allow only the public ports needed for HTTP certificate validation and HTTPS. Provider firewall policy and the host firewall are separate controls. See [Chapter 27](../03-networking-and-traffic/027-firewalls-and-network-policy.md) and [Chapter 29](../03-networking-and-traffic/029-load-balancers-and-traffic-distribution.md) for those boundaries.

## Route to the loopback upstream

On Ubuntu Server 24.04, install Nginx with `sudo apt update && sudo apt install nginx`; place the site in `/etc/nginx/sites-available/dispatchdesk` and enable it with a symlink under `/etc/nginx/sites-enabled/` after confirming the packaged `nginx.conf` includes that directory. On Fedora or RHEL 9, check the supported Nginx package or module stream for that exact release (`dnf module list nginx` on modular systems; on RHEL, confirm the required subscription and AppStream access), then install `nginx`; place a server fragment under `/etc/nginx/conf.d/` after checking `nginx -T` for the active include. Both families use the `nginx` systemd unit in these examples. Package availability and stream names can change, so follow the release-specific distribution guide. These commands change host packages and service state; do not run them on production without the Chapter 31 access, backup and maintenance plan. In the appropriate `http` context, define an upstream and a server block. Replace `orders.example.test` with the hostname you control.

```nginx
upstream dispatchdesk_app {
    server 127.0.0.1:8080;
    keepalive 16;
}

server {
    listen 80;
    listen [::]:80;
    server_name orders.example.test;

    location / {
        proxy_pass http://dispatchdesk_app;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 3s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        client_max_body_size 64k;
    }
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    return 444;
}
```

Use exactly one `default_server` for each address and port. Ubuntu's packaged `sites-enabled/default` commonly already declares one, so do not enable this catch-all unchanged alongside it. Before enabling the site, inspect the loaded configuration with `sudo nginx -T` and the enabled-site symlinks with `ls -l /etc/nginx/sites-enabled/`. Either edit the existing default server to reject unmatched Host values, or preserve its configuration and disable only that known vendor-default symlink after confirming it is not serving another site; then enable the catch-all above. Keep the previous file and link target so rollback can restore the original site, remove the new catch-all, and re-run `nginx -t` before reload. On Fedora/RHEL, perform the same inventory under `conf.d`; merge the rejection into an existing default block instead of creating a duplicate listener.

After placing and enabling the fragment, check the complete configuration and start the service if it is not already running:

```bash
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl status --no-pager nginx
```

On an enforcing Fedora/RHEL host, SELinux can deny Nginx's connection to the loopback application even when the app is listening correctly. Check for a matching AVC denial and inspect the current boolean before changing policy:

```bash
sudo ausearch -m AVC -ts recent
getsebool httpd_can_network_connect
```

If evidence confirms this denial and the security owner approves the broader permission, `sudo setsebool -P httpd_can_network_connect on` persists a policy allowing the web-server domain to initiate network connections. That permission is broader than this one upstream; a narrowly scoped local policy may be more appropriate on a hardened host. Preserve the prior value. If it was off and the approved change must be rolled back, use `sudo setsebool -P httpd_can_network_connect off`; do not disable SELinux. A 502 without a corresponding AVC can have other causes, so check Nginx's error log, the upstream address, service state and local request path too.

An `upstream` group gives a stable name to the backend set; here it contains one local process. `proxy_pass` forwards requests. The headers preserve host and forwarding context, but the application must trust them only when they arrive from a known proxy. A client can send its own `X-Forwarded-For` header. If the application accepts that value blindly, callers can forge their apparent address. Configure trusted proxy hops explicitly in the application and any log pipeline.

The 64 KiB limit matches the future DispatchDesk HTTP contract from Chapter 10. It limits body size at this proxy layer, not total memory consumed by parsing, buffering or application work. Align every upstream limit and return a useful client error for excess bodies. A request that is allowed here can still exceed an application's own limit or deadline.

Nginx timeouts represent different waits. The connect timeout bounds establishing an upstream connection; send and read timeouts bound inactivity while sending or receiving. In particular, `proxy_read_timeout` is the gap between successive reads, not a total request duration. A chatty streaming endpoint can remain open longer than that value. Set limits according to actual endpoint behavior, client deadlines and shutdown design rather than copying round numbers into production.

## Test configuration and the full request path

Validate configuration before asking Nginx to reload it:

```bash
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl status --no-pager nginx
sudo ss -ltnp
```

`nginx -t` checks parsing and attempts to open referenced files; it does not prove DNS, certificate trust, application correctness or public reachability. A reload asks a running service to adopt the new configuration while retaining its lifecycle. Check the service state and logs after reload. Confirm expected listeners: public port 80 during this stage, loopback port 8080 for DispatchDesk, and no accidental public application listener. Use the distribution's service name if it differs.

Test from the host, then from a separate network. On the host, query the HTTP endpoint and check the Host routing behavior. From an external client, verify DNS resolution, provider ingress, host firewall, TLS once configured, proxy routing and application response. This sequence helps identify which layer failed. A local `curl` to `127.0.0.1` cannot test a provider security group or public DNS.

For TLS, use a certificate for the exact hostname, install its private key with restrictive ownership and permissions, and configure an HTTPS server block with the certificate chain and key files. Certificate issuance and renewal depend on DNS, validation method and client tooling. A certificate file that exists today is not proof that renewal will work. Test automated renewal in a controlled environment and alert on expiry. Redirect cleartext HTTP only after the required certificate challenge flow is understood. Do not put a private key into source control, chat, an image or world-readable configuration.

An HTTPS listener typically forwards a fixed trusted scheme to the backend once TLS is terminated at Nginx. The HTTP example above forwards `$scheme`; behind a separate TLS terminator, `$scheme` may represent the internal hop rather than the original public connection. Configure this only for the actual topology. Do not trust a caller-provided forwarded-proto header when there is no trusted proxy boundary.

## Buffering, long requests and multiple applications

Nginx response buffering can decouple a fast upstream from a slower client and may use temporary disk files for large responses. That behavior can improve ordinary request handling, but it consumes memory and disk and can change streaming behavior. Disable buffering only for a route that requires streaming, and test backpressure and disconnect handling. Request buffering, response buffering and body-size limits are separate decisions; document the endpoint contract.

A single proxy can serve several applications by matching hostnames and sending each to a distinct private upstream. Give each server block an explicit `server_name`, a deliberate default server, and narrowly scoped locations. A typo or unmatched Host should not fall through to a sensitive application. Health endpoints also need thought: an internal monitoring check may require access without making diagnostic details public. Return minimal public health information and use an authenticated or private monitoring path for deeper diagnostics.

WebSocket upgrades, gRPC, streaming uploads and large downloads have protocol-specific requirements. Do not assume the basic HTTP directives fully support them. Review the relevant Nginx module documentation and application behavior before enabling such routes. A proxy is also not an application firewall: request validation, authentication, authorization, CSRF policy and rate limits remain explicit application or edge controls.

## Diagnose common failures

If Nginx returns `502`, inspect the Nginx error log and verify that DispatchDesk is active and listening at the configured address. A refused upstream connection commonly means there is no listener or the address/port is wrong. If Nginx returns `504`, inspect the application's dependency waits and endpoint deadline; raising the proxy timeout may only make clients wait longer. A `413` points toward a body-size limit. A successful local response with a failed external connection points toward DNS, routing or firewall layers.

If the client sees the wrong scheme or address in application logs, inspect every trusted proxy hop and the forwarding-header policy. Compare the received Host with expected virtual hosts. If a configuration change breaks all sites, restore the last known-good file from controlled configuration management, validate it, and reload. Keep a separate copy of the previous working configuration; avoid broad `sed` commands against live configuration.

## Exercises and review questions

1. Draw the request path from an external client to the Python process. Label DNS, provider ingress, host firewall, Nginx, loopback and application.
2. What could a client forge in `X-Forwarded-For`? Describe the exact trusted-proxy policy needed before using it for security decisions.
3. An endpoint emits a heartbeat every 20 seconds and runs for three minutes. How would the read timeout behave? What separate overall deadline should the client and service enforce?
4. Add a second fictional hostname without making either app listen publicly. Identify how an unmatched Host is handled.

**Answer guidance:** Keep the application on loopback and allow the host firewall only the intended public proxy ports. Rebuild or trust `X-Forwarded-For` only from a known proxy hop; strip untrusted incoming values so callers cannot invent their source address. `proxy_read_timeout` measures the idle interval between upstream reads, not total elapsed request time, so a streaming response can run longer; apply an absolute deadline in the application or an outer request policy. For a 502, correlate Nginx's error log with the local socket, systemd journal and SELinux AVC records before changing policy; the enforcing-mode boolean is broader than a single backend and should be enabled only under approved policy. The default server block should reject unknown Host values instead of forwarding them to DispatchDesk, then be tested with both valid and unrelated names.

Reliable proxying depends on an explicit upstream, trusted forwarding metadata and limits aligned with application behavior. The next chapter examines the database and cache on the same constrained host, where network isolation alone is not enough to manage resource contention.

## Sources and verification

Nginx's official [`ngx_http_proxy_module`](https://nginx.org/en/docs/http/ngx_http_proxy_module.html) and [`ngx_http_upstream_module`](https://nginx.org/en/docs/http/ngx_http_upstream_module.html) documentation and Red Hat's [RHEL 9 reverse-proxy procedure](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/deploying_web_servers_and_reverse_proxies/setting-up-and-configuring-nginx_deploying-web-servers-and-reverse-proxies) were inspected on 2026-10-04. Nginx is absent, so `nginx -t` and live proxy exchanges were not performed. No package was installed, certificate issued, public firewall opened or application started.
