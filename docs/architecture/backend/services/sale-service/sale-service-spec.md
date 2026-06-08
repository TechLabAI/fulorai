---
service: sale-service
module: SALE
type: standard
package: com.journeyos.sale
gradleKey: ":services:sale-service"
port: 8086
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
  - adr/ADR-005-revenue-attribution-model.md
---

# SALE — Sales & Revenue Spec (sale-service)

> **Full spec set.** SALE owns the **sales pipeline (CRM)**, **offers**, **purchases/revenue**,
> **revenue attribution** and **LTV** inside each `empresa` (schema `emp_<slug>`). It depends on WRKS
> for tenant context + authorization and on LEAD (events) to open opportunities. Attribution and LTV
> are **deterministic** — no TechLab AI in the MVP. SALE records confirmed purchases; it does **not**
> process payment. EARS notation guide: `docs/architecture/backend/standards/ears-notation.md`.

## Purpose

Turn scattered closings (DM, call, checkout) into a **traceable, explainable, auditable revenue
funnel**. SALE manages opportunities through a configurable pipeline, recognizes revenue from
idempotent purchase ingestion, attributes each real to its touchpoints (source/journey/campaign) via
a versioned deterministic model, computes per-contact LTV, and publishes domain events that INTL
(analytics), WRKS (audit) and COMM (post-sale) react to.

## Spec map

| SPEC | Theme | Status |
|---|---|---|
| [SPEC-01](spec/backend/SPEC-01-api-surface.md) | API surface (`/oportunidades/**`, `/ofertas`, `/compras`, `/atribuicao`, `/ltv`) | draft |
| [SPEC-02](spec/backend/SPEC-02-sales-pipeline-orchestration.md) | Sales pipeline orchestration (core: opportunity → purchase → revenue) | draft |
| [SPEC-03](spec/backend/SPEC-03-revenue-attribution-ltv.md) | Revenue attribution + LTV — deterministic, explainable | draft |
| [SPEC-04](spec/backend/SPEC-04-data-model-migrations.md) | Data model + migrations (`emp_<slug>`) | draft |
| [SPEC-05](spec/backend/SPEC-05-idempotency-concurrency.md) | Idempotency + concurrency (purchase dedup, re-attribution) | draft |
| [SPEC-06](spec/backend/SPEC-06-security.md) | Security (JWT resource server, `sale.*` permissions, LGPD) | draft |
| [SPEC-07](spec/backend/SPEC-07-observability-health.md) | Observability + health | draft |
| [SPEC-08](spec/backend/SPEC-08-bdd-test-scenarios.md) | BDD test scenarios | draft |
| [SPEC-09](spec/backend/SPEC-09-messaging-architecture.md) | Messaging (Kafka) — produced `oportunidade.*`/`compra.*` + consumed LEAD/WRKS | draft |
| [SPEC-10](spec/backend/SPEC-10-integrations.md) | Integrations (WRKS, LEAD, Elasticsearch, checkout, MIG, Eureka) | draft |

## Contracts

- `contracts/api-contract.md` — REST surface + ProblemDetail errors
- `contracts/data-model.md` — pipeline/revenue DDL (`-- schema: empresa`)
- `contracts/event-contracts.md` — produced/consumed events
- `contracts/hub-integration.md` — inter-service (WRKS, LEAD, downstream consumers)
- `contracts/integration-contracts.md` — external systems (Elasticsearch, checkout; no AI in MVP)

## Key references

- `docs/architecture/shared/multi-empresa.md`, `docs/architecture/shared/modelo-dados/{empresa,relacionamentos}.md`
- `docs/architecture/shared/contratos/error-model.md`
- WRKS (dependency): `docs/architecture/backend/services/wrks-service/contracts/`
- LEAD (upstream events): `docs/architecture/backend/services/lead-service/contracts/event-contracts.md`
