# 01 — Architectural Vision (REG · journey-os-service-registry)

> Module type: **infra / registry**. This vision is intentionally minimal — REG has no business domain.

## 1. Intent

Provide the Journey OS backend with a **single, well-known service-discovery authority** (Netflix Eureka Server) so that microservices and the API Gateway locate each other dynamically — by logical service name, never by hardcoded host/port — across local, staging and production environments.

## 2. Problem Statement

In a multi-service backend (WRKS, LEAD, JRNY, ASST, COMM, SALE, INTL, GWY), instances come and go (scaling, deploys, restarts) and their network locations are not stable. Hardcoding URLs is brittle and blocks horizontal scaling. The backend needs a runtime registry where each instance announces itself and from which any caller can resolve healthy instances of a target service.

## 3. Personas

- **Microservice (machine, primary):** registers itself on startup, sends heartbeats, fetches the registry to resolve peers. Consumed transparently via Spring Cloud + OpenFeign.
- **API Gateway / GWY (machine):** resolves downstream routes from the registry.
- **Platform / DevOps / SRE operator (human, secondary):** opens the Eureka dashboard to see which services are UP/DOWN during operations and incidents.

## 4. MVP Scope (in)

- Standalone single-node **Eureka Server** (`@EnableEurekaServer`).
- Listens on **port 8761**; reachable in-cluster as `journey-os-service-registry:8761`.
- Eureka **dashboard** served at `/`.
- **Actuator** `health` and `info` endpoints exposed.
- Self-preservation and eviction tuned per profile (relaxed for `local`, default for `prod`).
- Server **does not register with or fetch from itself**.
- Fully environment-driven configuration (`${VAR}`), no secrets in source.

## 5. Out of Scope (MVP)

- Peer-to-peer / multi-zone HA replication and clustering.
- Authenticating or securing the dashboard behind an IdP / full RBAC.
- Alternative discovery backends (Consul, Zookeeper, Kubernetes DNS).
- Persistent storage of the registry (registry is in-memory and volatile by design).
- Custom eviction / lease policies beyond Eureka knobs.

## 6. Architectural Principles

- **Infra, not domain:** zero business logic, zero persistence, zero multi-tenancy, zero messaging.
- **Thin and boring:** a near-vanilla Spring Cloud Netflix Eureka Server; configuration over code.
- **Stateless & volatile:** the registry is rebuildable purely from clients re-registering.
- **Upstream dependency:** REG must be available before/independently of business services; it depends on no other Journey OS service.
- **Twelve-factor config:** all tunables via environment variables and Spring profiles.

## 7. Success Signals

- Every microservice appears as **UP** in the dashboard within its heartbeat window after startup.
- GWY and Feign clients resolve targets **by logical name** with no hardcoded URLs in non-local profiles.
- `GET /actuator/health` returns `UP` and is suitable as a container/orchestrator probe.
- A restarted client re-registers automatically and reappears in the registry without operator action.
