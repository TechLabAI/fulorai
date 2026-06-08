---
service: lead-service
module: LEAD
type: standard
package: com.journeyos.lead
gradleKey: ":services:lead-service"
port: 8082
status: draft
specSet: full
ears: true
sourceVision:
  - 01-architectural-vision.md
  - 02-architecture-blueprint.md
  - 03-initial-domain-framing.md
  - 04-backend-architecture-direction.md
  - 05-persistence-model.md
  - 06-risks-gaps-assumptions.md
adrs:
  - adr/ADR-001-hexagonal-architecture.md
  - adr/ADR-002-single-service-boundary.md
  - adr/ADR-003-messaging-strategy.md
  - adr/ADR-004-multitenant-strategy.md
  - adr/ADR-005-maturity-score-model.md
---

# LEAD — Lead Intelligence & Qualification Spec (lead-service)

> **Full spec set.** LEAD owns the **lead** aggregate inside each `empresa` (schema `emp_<slug>`):
> capture/dedup, profile, surveys, versioned qualification rules, the **Maturity Score (6D)** and
> dynamic segmentation. It depends on WRKS for tenant context + authorization and delegates AI to
> TechLab AI (capability `qualification`, optional assist with deterministic fallback).
> EARS notation guide: `docs/architecture/backend/standards/ears-notation.md`.

## Purpose

Turn a fragmented stream of captured contacts into a **prioritized, explainable, routable queue**.
LEAD deduplicates leads, builds a typed profile, applies versioned qualification rules, computes the
6-dimension Maturity Score (with breakdown), groups leads into dynamic segments, and publishes domain
events that JRNY (routing), SALE (prioritization), COMM (nurturing) and INTL (analytics) react to.

## Spec map

| SPEC | Theme | Status |
|---|---|---|
| [SPEC-01](spec/backend/SPEC-01-api-surface.md) | API surface (`/api/v1/leads/**`, `/surveys`, `/qualification`, `/segments`) | draft |
| [SPEC-02](spec/backend/SPEC-02-lead-qualification-orchestration.md) | Lead qualification orchestration (core: capture → qualify → segment) | draft |
| [SPEC-03](spec/backend/SPEC-03-maturity-score-6d.md) | Maturity Score (6D) — deterministic, explainable, AI-assisted | draft |
| [SPEC-04](spec/backend/SPEC-04-data-model-migrations.md) | Data model + migrations (`emp_<slug>`) | draft |
| [SPEC-05](spec/backend/SPEC-05-idempotency-concurrency.md) | Idempotency + concurrency (capture dedup, score recompute) | draft |
| [SPEC-06](spec/backend/SPEC-06-security.md) | Security (JWT resource server, `lead.*` permissions, LGPD) | draft |
| [SPEC-07](spec/backend/SPEC-07-observability-health.md) | Observability + health | draft |
| [SPEC-08](spec/backend/SPEC-08-bdd-test-scenarios.md) | BDD test scenarios | draft |
| [SPEC-09](spec/backend/SPEC-09-messaging-architecture.md) | Messaging (Kafka) — produced `lead.*` + consumed WRKS events | draft |
| [SPEC-10](spec/backend/SPEC-10-integrations.md) | Integrations (WRKS, TechLab AI, Elasticsearch, MIG, Eureka) | draft |

## Contracts

- `contracts/api-contract.md` — REST surface + ProblemDetail errors
- `contracts/data-model.md` — lead DDL (`-- schema: empresa`)
- `contracts/event-contracts.md` — produced/consumed events
- `contracts/hub-integration.md` — inter-service (WRKS, downstream consumers)
- `contracts/integration-contracts.md` — external systems (TechLab AI, Elasticsearch)
- `contracts/techlab-ai-integration.md` — capability `qualification` (assist + fallback)

## Key references

- `docs/architecture/integrations/techlab-ai-integration.md`
- `docs/architecture/shared/multi-empresa.md`, `docs/architecture/shared/modelo-dados/{empresa,relacionamentos}.md`
- `docs/architecture/shared/contratos/error-model.md`
- WRKS (dependency): `docs/architecture/backend/services/wrks-service/contracts/`
