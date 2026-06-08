# 04 — Backend Architecture Direction (REG · journey-os-service-registry)

## 1. Stack

- **Java 21**, **Spring Boot 3.5.x**.
- **Spring Cloud Netflix Eureka Server** (`spring-cloud-starter-netflix-eureka-server`), Spring Cloud version aligned with the monorepo BOM.
- **Spring Boot Actuator** (health/info).
- Gradle 8.x (Kotlin DSL), as a subproject of the backend monorepo (`:services:journey-os-service-registry`).
- **No** PostgreSQL, **no** Artemis/Kafka, **no** JPA. (Eureka is a *client* of itself only conceptually; the server depends on none of these.)

## 2. Service Boundary

**Single, standalone service.** No decomposition. REG is a dedicated process whose only responsibility is service discovery. It is intentionally separated from GWY so the gateway can be scaled/redeployed independently of the registry.

## 3. Package Organization

The standard hexagonal `api/application/domain/infrastructure` split **does not apply** — there is no domain. Reduced structure:

```
com.journeyos.reg/
└── RegistryApplication.java   // @SpringBootApplication @EnableEurekaServer
```

Plus configuration under `src/main/resources/` (`application.yml` + profile overlays). RULE-09 (mandatory base package `com.journeyos.reg`) applies; the layer-dependency rules (RULE-01..06, RULE-08) are non-applicable because those layers do not exist (recorded in ADR-001).

## 4. Hub Service Dependencies

**None.** REG does not call WRKS or any other Journey OS service. The dependency direction is inverted: every other service depends on REG at runtime (as a Eureka client), but REG depends on no one.

## 5. External Integrations

- **None outbound.**
- **Inbound:** Eureka registration/discovery protocol from all backend clients and GWY. No TechLab AI, no third-party APIs.

## 6. Async vs Sync Decisions

- The Eureka protocol is **synchronous HTTP** (register, heartbeat, fetch) — framework-managed.
- **No messaging** (no Artemis/Kafka producers or consumers). REG does not participate in any saga or event flow.
- Self-preservation / eviction timing is the only "async" behavior and is governed by Eureka configuration (see ADR-005).
