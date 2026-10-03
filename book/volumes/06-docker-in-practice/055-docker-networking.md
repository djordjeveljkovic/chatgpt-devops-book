---
book: The Complete DevOps Engineering Book
volume: 6
volume_title: "Docker in Practice"
chapter: 55
title: "Docker Networking"
slug: docker-networking
status: complete
summary: ../../_ai/chapter-summaries/055-docker-networking.md
---

# Chapter 55 — Docker Networking

A container has network interfaces, routes, name resolution and firewall rules just like a process on another Linux host, but Docker creates and manages much of that configuration. The common mistake is to treat a container's port number as if it were automatically open on the Docker host. A second mistake is to put every service on one shared network and assume that network membership provides application authentication. This chapter traces traffic through bridge, host and published-port choices, then uses a private user-defined bridge to test communication by service name.

The examples assume a Linux Docker Engine on a disposable host and an ordinary user authorized to access its intended local daemon. Run host commands and any `curl 127.0.0.1` checks on the Docker host. If the active context is remote, the container and published socket are on the remote daemon host; a local loopback request from the CLI workstation does not test that remote listener. Docker Desktop and rootless networking add their own forwarding layers, so verify those separately.

## Bridge, host and user-defined networks

Docker creates a default bridge network. Containers attached to it can communicate using addresses, but Docker's built-in name resolution between containers is provided on a user-defined bridge. For small applications, create one bridge per trust boundary or compose stack and connect only the required services. A user-defined bridge gives containers on the same Docker host private addresses, automatic DNS for container names and network-level separation from containers on unrelated Docker networks. It does not encrypt traffic, authenticate callers, or prevent a compromised member from trying every listening port on its peers.

The host network driver removes the separate container network namespace for networking: the process shares the host network stack. Host-mode containers do not use ordinary port publishing, because their sockets bind directly in the host namespace. This can reduce one layer of address translation for specific workloads, but it also removes useful isolation and makes port conflicts host-level conflicts. Support details differ by platform and Engine configuration. Use bridge networking unless you have a measured need for host mode and understand its exposure.

The `none` network driver leaves a container without ordinary external network connectivity. It can suit a build or batch task that needs no network, but test required loopback or mounted-socket behavior explicitly. Overlay networking connects services across multiple Docker hosts when configured for a supported cluster mode; a local bridge is scoped to one daemon host. Kubernetes, Swarm, cloud VPCs and other platforms each supply their own network model and policy, which should not be inferred from this local lab.

List the networks and inspect the bridge selected by a container:

```bash
docker network ls
```

An address in `NetworkSettings` is private network metadata, not a stable service endpoint. Container IP addresses can change when the container is recreated. Use a DNS name or alias on a user-defined bridge for service-to-service discovery, and use a managed discovery mechanism outside the one-host Docker domain. The inspection command appears after the lab creates its container below.

## Service naming and published ports

A container listening on port 8080 is reachable on that port by peers sharing its network, subject to the listener binding and network configuration. It does not need `--publish` for that container-to-container path. Publishing creates a host-facing mapping. In `--publish 127.0.0.1:18081:8080`, Docker forwards host loopback port 18081 to container port 8080. Omitting the host address usually binds the published port on all host addresses, making it reachable from other machines permitted by network routing and firewall policy. Consult the current Docker port-publishing docs for IPv4, IPv6 and gateway-mode behavior.

Loopback publication is a useful boundary for local testing, but verify the Engine version and configuration. Docker documents a same-layer-2 reachability caveat for localhost-published ports before Engine 28.0.0. Host firewall integration also matters: published ports can bypass assumptions made from a UFW or firewalld rule inspection. Treat the mapping, packet-filter backend, cloud firewall and host routing as one exposure path. A published port does not add TLS or application authentication.

On a user-defined bridge, a client container can connect to the service using its container name or configured network alias. Keep database ports private by connecting only the API and database to the intended bridge, and authenticate at the database regardless of network placement. If a second network is needed for the web edge, attach the API to both appropriate networks and keep the database off the edge network. Network membership is a reachability control, not a substitute for authorization, secrets management or least privilege.

## Debugging communication between containers

On the disposable Docker host, create a uniquely named network and a small Nginx service. This lab uses a mutable learning image tag, pulls images if absent and changes the daemon's local network state. It publishes no host port:

```bash
docker network create dispatchdesk-lab-net
docker run --detach --name dispatchdesk-lab-web \
  --network dispatchdesk-lab-net nginx:alpine
```

Inspect its network attachment after creation:

```bash
docker inspect dispatchdesk-lab-web --format '{{json .NetworkSettings.Networks}}'
```

Test from a short-lived client container on the same user-defined bridge:

```bash
docker run --rm --network dispatchdesk-lab-net busybox:1.36 \
  wget -qO- http://dispatchdesk-lab-web/
```

The request should return Nginx's default page. No host port is published: the client resolves the service name using the user-defined network's embedded DNS, then connects to the service's port 80. The disposable BusyBox client uses `--rm`, so it disappears after its request; its stdout is the response evidence. The Nginx service remains for inspection. This is only a network reachability test and does not prove a DispatchDesk API health check, database authorization or external ingress behavior.

Inspect membership, address and logs when the request fails:

```bash
docker network inspect dispatchdesk-lab-net
docker inspect dispatchdesk-lab-web --format '{{.State.Status}} {{json .NetworkSettings.Networks}}'
docker logs --tail 50 dispatchdesk-lab-web
```

If name lookup fails, confirm both containers are attached to the same user-defined network and that the service name or alias is correct. If lookup works but the connection fails, check whether the process is running, which address it listens on, and which port it opened. If the service works from a peer container but not from the workstation, inspect published-port configuration and host-side policy; network membership alone does not publish it. If it works on the host but not from an external client, check bind address, host routes, cloud security rules and firewall behavior. Compare evidence at each hop instead of replacing the container IP with a guessed permanent address.

Remove only the named lab service and network when finished:

```bash
docker stop dispatchdesk-lab-web
docker rm dispatchdesk-lab-web
docker network rm dispatchdesk-lab-net
```

The network removal fails while containers remain attached, which is a useful guard. The commands do not remove downloaded images. Do not run broad `docker network prune` commands on a shared host to clean up one exercise.

## Exercises and review questions

1. Why can two containers on a user-defined bridge communicate without publishing a host port?
2. What behavior usually changes when `--publish 8080:80` omits a host address?
3. The HTTP request works by container name from a peer, but not from your laptop. Which boundary does that evidence narrow down?
4. Why does attaching a database and an untrusted web-facing container to the same bridge not constitute database authorization?
5. What additional exposure caveat applies to localhost-published ports on Docker Engine versions before 28.0.0?

### Answer guidance

1. Same-network peers can reach listening ports on one another's container interfaces; publishing is for a host-facing mapping.
2. The host mapping generally binds all host addresses, subject to daemon settings and host/network policy.
3. Container DNS and bridge reachability work; inspect publication, daemon host, host firewall, routes and external firewall policy.
4. Network peers can attempt all listening ports, and a compromised member can send traffic. The database still needs credentials and authorization, with narrower network membership where possible.
5. Docker documents that peers on the same layer 2 segment could reach such ports before 28.0.0; check the deployed Engine version and current port-publishing guidance.

## Takeaways

- A user-defined bridge provides service-name resolution and a useful one-host reachability boundary.
- Container-to-container traffic does not require host port publication; published ports create a separate exposure path.
- Host networking shares the host network stack, while `none` removes ordinary network connectivity.
- Test DNS, process listening state, container port, publication, host firewall and upstream routing as separate boundaries.
- Network membership does not replace authentication, encryption or application authorization.

## Further reading

- [Running and Managing Containers](052-running-and-managing-containers.md) — container lifecycle and published-port examples.
- [Docker Volumes and Persistent Data](056-docker-volumes-and-persistent-data.md) — state shared outside network paths.
- [Firewalls and Network Policy](../03-networking-and-traffic/027-firewalls-and-network-policy.md) — host and network filtering foundations.

## Sources and verification

Docker's [bridge driver](https://docs.docker.com/engine/network/drivers/bridge/), [host driver](https://docs.docker.com/engine/network/drivers/host/), [port publishing](https://docs.docker.com/engine/network/port-publishing/) and [firewall integration](https://docs.docker.com/engine/network/packet-filtering-firewalls/) documentation were inspected on 2026-10-02. The localhost version caveat and default host binding behavior reflect that inspection date. Commands are reader-run and were not executed because the workspace has no Docker daemon; actual firewall, DNS and rootless/Desktop behavior must be checked on the target host.
