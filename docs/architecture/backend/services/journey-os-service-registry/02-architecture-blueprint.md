# 02 — Architecture Blueprint (REG · journey-os-service-registry)

## 1. System Boundary

REG is a standalone **Eureka Server** process. Its boundary is the Eureka registration/discovery protocol over HTTP (`/eureka/*`) plus the dashboard (`/`) and Actuator (`/actuator/*`). It owns no database, no broker connection, and no tenant context.

```
┌─────────────────────────────────────────────┐
│  journey-os-service-registry  (port 8761)    │
│  ┌─────────────────────────────────────────┐ │
│  │  Eureka Server (in-memory registry)      │ │
│  │   • /eureka/*  registration + discovery  │ │
│  │   • /          dashboard (UI)            │ │
│  │   • /actuator/health,info                │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
        ▲ register/heartbeat        ▲ fetch registry
        │                           │
  [ all microservices ]      [ GWY, Feign clients ]
```

## 2. External Actors and Systems

| Actor | Interaction | Direction |
|---|---|---|
| Backend microservices (WRKS, LEAD, JRNY, ASST, COMM, SALE, INTL) | Register, heartbeat, fetch registry | inbound to REG |
| GWY (API Gateway) | Fetch registry to resolve routes | inbound to REG |
| DevOps/SRE operator | View dashboard / health | inbound to REG |
| Container orchestrator (Docker Compose / ECS / K8s) | Liveness/readiness probe via `/actuator/health` | inbound to REG |

REG makes **no outbound calls** to any Journey OS service or external system.

## 3. End-to-End Flows

**Golden path — client registration & discovery:**
1. REG starts and exposes Eureka endpoints on 8761.
2. A microservice boots with `eureka.client.service-url.defaultZone=http://journey-os-service-registry:8761/eureka/`.
3. The client POSTs its instance (app name, IP/host, port, status) → REG stores it in the in-memory registry.
4. The client sends periodic heartbeats; REG renews the lease.
5. A caller (GWY / Feign) fetches the registry and resolves a healthy instance of the target service by logical name.

**Alternative — client shutdown / failure:**
- Graceful: client de-registers on shutdown → REG removes it.
- Crash: heartbeats stop → REG evicts the lease after the expiry window (governed by self-preservation settings).

**Alternative — local dev without registry:**
- Clients set `eureka.client.enabled=false` and use explicit Feign URLs (see `platform-patterns.md` §7.2). REG is then optional locally.

## 4. Internal Boundaries

REG does **not** use the hexagonal `api/application/domain/infrastructure` layering — there is no domain to isolate. Internal structure is minimal:

- `RegistryApplication` — `@SpringBootApplication @EnableEurekaServer` entry point (package `com.journeyos.reg`).
- Configuration lives entirely in `application.yml` + profile overlays (`application-local.yml`, `application-prod.yml`).

> The ArchUnit business rules (RULE-01..06, RULE-08) are largely **non-applicable** here because the corresponding layers/dependencies do not exist. RULE-09 (base package `com.journeyos.reg`) still applies. See ADR-001.

## 5. Cross-cutting Concerns

- **Security:** dashboard/endpoints are network-restricted (cluster-internal) in MVP; no app-level auth. Hardening (auth on dashboard, mTLS between clients and registry) is explicitly out of scope. See `06-risks-gaps-assumptions.md`.
- **Observability:** Actuator `health`/`info`; logs follow the standard console pattern; `service` MDC field = `journey-os-service-registry`. No correlation-id propagation needed (REG initiates no business requests).
- **Multi-tenancy:** **none.** REG is tenant-agnostic infrastructure. See ADR-004.
- **Resilience:** single-node in MVP (acceptable SPOF for early phases); HA via peer replication is a documented future step (ADR-005 / risks).
