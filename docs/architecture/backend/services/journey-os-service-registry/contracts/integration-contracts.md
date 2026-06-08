# Integration Contracts — journey-os-service-registry (REG)

> REG makes **no outbound integrations** (no third-party APIs, no Hub Feign calls, no
> TechLab AI). Its only "integration" is **inbound**: backend services registering as
> Eureka clients. This document defines the contract clients must honor.
> EARS guide: `docs/architecture/backend/standards/ears-notation.md`.

## 1. External systems

**None outbound.** REG depends on no external system. No OAuth2 client_credentials, no
certificates, no rate-limited third-party APIs.

## 2. Inbound integration — Eureka client registration contract

Every Journey OS backend service (WRKS, LEAD, JRNY, ASST, COMM, SALE, INTL, GWY) integrates
with REG by acting as a Eureka **client**. Canonical client config (`platform-patterns.md` §7):

```yaml
eureka:
  client:
    service-url:
      defaultZone: ${EUREKA_URL:http://journey-os-service-registry:8761/eureka/}
    register-with-eureka: true
    fetch-registry: true
  instance:
    prefer-ip-address: true
    instance-id: ${spring.application.name}:${random.value}
```

### Contract requirements (EARS)

- THE client SHALL set `spring.application.name` to its logical service name (used as the Eureka `appName`).
- WHEN a client boots with `register-with-eureka: true`, THE client SHALL register with REG at `defaultZone` and begin heartbeats.
- WHILE a client is running, THE client SHALL renew its lease within the configured heartbeat interval.
- WHEN a client shuts down gracefully, THE client SHALL de-register from REG.
- IF REG is unreachable at client startup, THEN THE client SHALL retry registration per Spring Cloud defaults and serve from its cached registry where possible.

### REG-side obligations (EARS)

- WHEN REG receives a valid registration, THE SYSTEM SHALL make the instance discoverable via `GET /eureka/apps`.
- IF an instance's lease expires (missed heartbeats beyond the eviction window), THEN THE SYSTEM SHALL evict it, subject to self-preservation (ADR-005).

## 3. Resilience / fallback

- REG itself has no downstream to protect with circuit breakers/retries (it calls nothing).
- **Client-side resilience:** clients cache the registry; if REG is temporarily down, existing routing continues from cache. Single-node REG is a documented SPOF (R1) mitigated this way until HA (ADR-005).

## 4. SLA

- Target: REG reachable on `:8761` whenever the cluster is up; `GET /actuator/health` = `UP`.
- No business SLA (no domain transactions). Availability is the only operational concern.
