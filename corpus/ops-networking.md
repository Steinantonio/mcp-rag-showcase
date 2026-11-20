---
id: ops-networking
title: Network access, VPN and egress
tags: networking, vpn, firewall, egress
---
## Getting on the network

Engineers reach internal services through the VPN, authenticated with the hardware key. The VPN grants access to
the private subnets but not to production databases, which live in a separate subnet reachable only from the
application tier.

Split tunnelling is disabled. If the VPN is down, work that needs internal access stops, and that is an accepted
cost of not exposing internal endpoints to the public internet.

## Egress rules

Outbound traffic is deny-by-default. A service that needs to call an external provider declares the destination in
its infrastructure definition, and the declaration is reviewed like code. Wildcard egress is rejected in review,
including during incidents.

If an incident requires a temporary egress rule, it is added with an expiry timestamp and removed by the same
person who added it. Rules without expiry become permanent, and permanent rules become the reason nobody can
answer "what can this service reach".

## Ingress

Public ingress terminates TLS at the edge and forwards to the service. Internal services are not exposed directly,
even inside the private network: the edge is the only place that knows about the outside world, which keeps the
blast radius of a misconfiguration small.

Health checks come from the load balancer and are allowed without authentication. They return a body of at most a
few hundred bytes and never touch a database.

## Debugging connectivity

The usual cause of a connectivity failure is a missing egress declaration, not a firewall bug. Check the service
definition first, then the DNS resolution, then the rule. Escalate to the network owner only after those three,
with the outputs attached.
