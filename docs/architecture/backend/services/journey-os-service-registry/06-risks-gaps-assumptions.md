# 06 — Risks, Gaps, Assumptions (REG · journey-os-service-registry)

## 1. Risks

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | **Single point of failure** — one Eureka node in MVP. If REG is down, new clients cannot register and stale callers rely on cached registries. | High (no new discovery) | Existing clients keep a cached registry and degrade gracefully; promote to peer-replicated HA before production scale (ADR-005, future). |
| R2 | **Unsecured dashboard/endpoints** — no app-level auth in MVP. | Medium (info disclosure of topology) | Restrict to cluster-internal network / security group; defer dashboard auth to a hardening issue (out of MVP scope). |
| R3 | **Self-preservation misconfiguration** — too aggressive eviction drops healthy instances during transient network blips; too lax keeps dead instances. | Medium (routing errors) | Profile-tuned settings (relaxed locally, default in prod); validated via dashboard observation (ADR-005). |
| R4 | **Client clock skew / heartbeat misconfig** flaps instances UP/DOWN. | Low–Medium | Standardize client `eureka.instance` settings via shared config (platform-patterns §7). |

## 2. Known Gaps

- No HA / peer replication in MVP (intentional).
- No persistence of the registry (intentional — volatile by design).
- No dashboard authentication (intentional — deferred to hardening).
- No automated alerting on mass de-registration (future observability work, likely owned by INTL).

## 3. Assumptions to Validate

- A1: Eureka (Netflix) is the chosen discovery mechanism for the whole backend (vs Consul / K8s-native) — confirmed by ADR-002.
- A2: Port **8761** and in-cluster DNS name `journey-os-service-registry` are stable across environments.
- A3: All business services will adopt the shared Eureka client config from `platform-patterns.md` §7.
- A4: Single-node REG is acceptable for the early (pre-production) phases of Journey OS.

## 4. Critical Dependencies

- **Spring Cloud release train** compatible with Spring Boot 3.5.x (provides the Eureka Server starter).
- **GWY** and all Feign-based integrations depend on REG being reachable to resolve services in non-local profiles.
- Container/orchestration platform must expose REG at a stable address before business services start.
