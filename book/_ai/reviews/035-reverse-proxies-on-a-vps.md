# Independent re-review — Chapter 35

Reviewer: review_volume3_021_025 (independent correction review)
Date: 2026-10-04
Reviewed body SHA256: ebe557a41404af619ec74925857ac81a86c01ff6f59eefdd6c80da0935b6c976

## Current scope and findings

Re-read the complete current manuscript and summary against prior findings. All material findings are resolved. The additional default-server paragraph explicitly inventories loaded configuration and enabled symlinks before enabling the fragment, requires exactly one default per address/port, permits editing the intentional existing default or disabling only a verified unused packaged default, retains the old file/link target for rollback and requires nginx -t before reload. It addresses Ubuntu and Fedora/RHEL inclusion paths without deleting unknown sites.

Previously corrected SELinux proxy-connect permission, install/include/initial-start prerequisites, answer guidance and removal of pending-review narrative remain correct. No new material findings.

## Fresh validation and limits

`python3 tools/check_book.py --chapters 35-35` passed on 2026-10-04: one draft, 3 shell syntax blocks and 1,333 global local links; no errors or warnings. Nginx remains unavailable; no nginx -t, live HTTP/TLS exchange, distro VM matrix, package transaction, symlink mutation, service start/reload or SELinux policy change performed. This correction review used current body/summary and recorded evidence; no new external-source inspection. Only this review record changed.

## Prior dated evidence retained

Inspected official Nginx proxy module and Red Hat RHEL 9 Nginx reverse-proxy procedure on 2026-10-03; the latter explicitly documents httpd_can_network_connect. Nginx is absent, so nginx -t and live proxy exchanges were not performed. No package installed, certificate issued, public firewall opened or application started.

Primary sources inspected:

- https://nginx.org/en/docs/http/ngx_http_proxy_module.html
- https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/deploying_web_servers_and_reverse_proxies/setting-up-and-configuring-nginx_deploying-web-servers-and-reverse-proxies

Scoped checker `python3 tools/check_book.py --chapters 31-35` passed on 2026-10-03: 1 YAML parse, 14 shell syntax blocks, 1,315 global local links, no errors/warnings. Parsing is not cloud-init schema or Nginx/systemd runtime validation. No Ubuntu/Fedora/RHEL VM matrix, provider build, paid resource, live recovery or production application test performed.

Verdict: approved
