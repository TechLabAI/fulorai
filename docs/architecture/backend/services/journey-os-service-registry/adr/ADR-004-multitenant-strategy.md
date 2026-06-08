# ADR-004 — Multi-tenancy strategy (tenant-agnostic)

- **Status:** accepted

## Context

Journey OS is multi-tenant with a schema-per-`empresa` strategy (`journeyos_global` + `emp_*`), and business services resolve tenant context via `EmpresaContextHolder` and Hibernate `multiTenancy: SCHEMA` (`platform-patterns.md` §5). The default ADR-004 for a domain module wires this strategy.

## Decision

REG is **explicitly tenant-agnostic**. It carries no `empresaId`, no `EmpresaContextHolder`, no schema routing, and stores no tenant-scoped data. Service-instance metadata (app name, host, port, status) is cross-cutting infrastructure shared by all tenants.

## Alternatives considered

1. **Per-tenant registries / namespacing instances by tenant** — meaningless for discovery: a microservice instance serves all tenants; partitioning the registry by tenant would break load balancing; rejected.
2. **Tenant-agnostic (chosen)** — correct for shared infrastructure.

## Consequences

- **Positive:** no tenancy plumbing, no `EmpresaContextHolder`, no DB; REG stays trivial and correct.
- **Negative:** REG cannot enforce tenant-level isolation of discovery — by design; isolation is a domain/API concern handled upstream at GWY and in business services.

## References

- `docs/architecture/backend/standards/platform-patterns.md` §5
- `docs/architecture/shared/multi-empresa.md`
- `05-persistence-model.md`
