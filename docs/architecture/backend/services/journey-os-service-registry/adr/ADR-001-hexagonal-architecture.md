# ADR-001 — Hexagonal architecture (applicability for an infra module)

- **Status:** accepted

## Context

The Journey OS backend mandates a hexagonal (ports & adapters) package layout and enforces it via ArchUnit (RULE-01..06, RULE-08). REG is an infra module: a thin Spring Cloud Netflix **Eureka Server** with no domain logic, no persistence, no API surface authored by us, and no inter-service calls.

## Decision

REG **adopts the mandatory base package** `com.journeyos.reg` (RULE-09) but **does not implement** the `api/application/domain/infrastructure` layering, because there is no domain or business behavior to isolate. The standard layer-dependency ArchUnit rules (RULE-01..06, RULE-08) are treated as **non-applicable** for this module and the architecture check is reduced accordingly (a package-name check for RULE-09 is sufficient).

## Alternatives considered

1. **Force full hexagonal skeleton anyway** — creates empty `domain/`, `application/`, `api/` packages with no content; pure ceremony, misleading, rejected.
2. **Different base package** — violates RULE-09 and the monorepo convention; rejected.
3. **Reduced structure + RULE-09 only (chosen)** — honors the one rule that applies, avoids dead scaffolding.

## Consequences

- **Positive:** minimal, honest structure; no misleading empty layers; faster scaffold/build.
- **Negative:** REG is an exception to the "every service is hexagonal" mental model — must be documented (here) so reviewers don't flag it as missing layers.

## References

- `docs/architecture/backend/standards/hexagonal-patterns.md`
- Root `CLAUDE.md` — Non-negotiable rules (RULE-01..09)
- `04-backend-architecture-direction.md` §3
