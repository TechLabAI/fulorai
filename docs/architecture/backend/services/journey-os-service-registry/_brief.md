# REG — Structured Brief

> Source of truth for `be-architect-specs`, `be-architect-backlog`, `be-architect-scaffold`.
> Module type: **infra / registry** (Eureka service discovery). No business domain.

| # | Item | Value |
|---|---|---|
| 1 | Canonical name / prefix | `journey-os-service-registry` / **REG** (package `com.journeyos.reg`) |
| 2 | Problem solved | Microservices need to find each other without hardcoded URLs. REG is the **Eureka Server** — the single source of truth for "who is alive and where", enabling client-side service discovery and load balancing across the Journey OS backend. |
| 3 | Personas | **Primary (machine):** every Journey OS microservice acting as a Eureka *client* (register + fetch registry). **Secondary (human):** Platform/DevOps/SRE operator inspecting the Eureka dashboard and health during incidents. |
| 4 | MVP scope (in) | Standalone Eureka Server (`@EnableEurekaServer`); registry dashboard at `/`; Actuator health/info; environment-driven config; self-preservation tuned per profile; does **not** register with itself; reachable at `journey-os-service-registry:8761`. |
| 5 | Out of scope (MVP) | Peer-to-peer HA clustering / multi-zone replication; authenticating/securing the dashboard with full IdP; Consul/Zookeeper/Kubernetes-native discovery; persistent registry storage; custom eviction policies beyond Eureka defaults. |
| 6 | Mandatory integrations | **Inbound:** all backend microservices register as Eureka clients (`eureka.client.service-url.defaultZone`). **Outbound:** none. **Consumer of discovery:** GWY (API Gateway) resolves routes via the registry; Feign clients resolve provider instances via the registry. |
| 7 | TechLab AI / module deps | **TechLab AI:** none. **Other modules:** all modules depend on REG operationally (as clients) but there are **no domain events** and no synchronous business contracts. REG is upstream infra. |
| 8 | Domain-anchor event | **N/A** — infra module, no business domain event. The only relevant lifecycle signal is Eureka-internal *service-instance registered / evicted* (not a Journey OS domain event, not published to the broker). |

## Notes for downstream stages

- **No domain model, no persistence, no migrations, no JPA, no multi-tenancy** inside REG. The Eureka in-memory registry is the only state and it is volatile by design.
- **No messaging** (Artemis/Kafka): REG neither produces nor consumes broker events.
- Hexagonal package layout does **not** apply in the business sense — the service is a thin Spring Cloud Netflix Eureka Server. Scaffold should emit a **reduced (registry) structure**: main app class + `application.yml` (+ profiles) + health, no `api/application/domain/infrastructure` business packages.
- Specs-validate (EARS → BDD) is **N/A** for this module.
