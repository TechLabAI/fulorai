# ADR-002 — Service discovery: Eureka vs Consul vs Kubernetes-native

- **Status:** accepted

## Context

The Journey OS backend is a set of Spring Boot microservices that must discover each other at runtime without hardcoded URLs, and the API Gateway (GWY) must resolve routes dynamically. A discovery mechanism must be chosen for the whole backend. The platform standards (`platform-patterns.md` §7) already assume Eureka client configuration.

## Decision

Use **Netflix Eureka** (`spring-cloud-starter-netflix-eureka-server`) as the service-discovery backend, hosted by this dedicated REG service. Clients use `spring-cloud-starter-netflix-eureka-client` with the shared config from `platform-patterns.md` §7. Feign integrations resolve providers by logical name through Eureka.

## Alternatives considered

1. **HashiCorp Consul** — richer (KV store, health checks, multi-DC) but adds an external operational dependency and a different client model; heavier than needed for the current scope.
2. **Kubernetes-native discovery (DNS / Services)** — excellent when fully on K8s, but couples discovery to the orchestrator and is unavailable for local/dev and non-K8s targets; the project targets Docker Compose locally and AWS at large.
3. **Eureka (chosen)** — first-class Spring Cloud integration, trivial OpenFeign resolution, zero external infra, well-understood operationally, matches the standards already written.

## Consequences

- **Positive:** seamless Spring Cloud + OpenFeign integration; no extra infra to operate; consistent local and cloud behavior; aligned with existing `platform-patterns.md`.
- **Negative:** Eureka is in maintenance mode and is Java/Spring-centric (non-JVM clients are awkward — not a concern for this all-Java backend); single-node REG is a SPOF until HA is added (ADR-005).

## References

- `docs/architecture/backend/standards/platform-patterns.md` §7 (Eureka)
- `01-architectural-vision.md`, `02-architecture-blueprint.md`
