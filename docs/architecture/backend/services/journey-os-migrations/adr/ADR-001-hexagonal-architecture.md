# ADR-001 — Hexagonal architecture

**Status:** accepted

## Context
Journey OS mandates hexagonal (ports & adapters) layering and a fixed base package
`com.journeyos.<module>`, enforced by ArchUnit (`:<service>:architectureCheck`). MIG is
an infrastructure service with almost no domain, so a "just a Flyway runner" shortcut is
tempting.

## Decision
MIG adopts the canonical hexagonal layout under `com.journeyos.mig`, even though most
layers are thin or empty:
- `api/` — actuator/health only (no domain controllers).
- `application/service/` — migration-run orchestration.
- `domain/model/` — tiny POJOs (`SchemaTarget`, `MigrationVersion`), zero Spring/JPA.
- `infrastructure/config/` + `infrastructure/persistence/` — Flyway, DataSource, tenant
  schema enumeration.
The ArchUnit `architectureCheck` task runs and must pass.

## Alternatives considered
- **Flat single-package utility:** rejected — violates RULE-09 and breaks repo-wide
  consistency / tooling assumptions.
- **No service, pure Gradle Flyway plugin:** rejected — loses Spring config, profiles,
  actuator health, and the standard run model used across the monorepo.

## Consequences
- (+) Uniform structure; ArchUnit and generators work unchanged.
- (+) Easy to grow if MIG later needs richer orchestration.
- (−) Some empty/near-empty packages — acceptable cost for consistency.

## References
- `docs/architecture/backend/standards/hexagonal-patterns.md`
- Global ADR-001 (hexagonal-architecture); RULE-01, RULE-02, RULE-09.
