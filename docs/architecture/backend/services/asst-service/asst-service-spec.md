---
service: asst-service
module: ASST
type: standard
package: com.journeyos.asst
gradleKey: ":services:asst-service"
port: 8083
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
  - adr/ADR-005-asset-versioning.md
---

# ASST — Asset Hub Spec (asst-service)

> **Full spec set.** ASST is the **content core**: the single repository of a workspace's
> content assets (landing pages, e-mails, creatives, scripts, documents). It owns the asset
> lifecycle (immutable versioning + approval/publication state machine), the Asset Studio
> (AI-assisted composition delegated to TechLab AI `document_composition`) and Asset
> Intelligence (auto-tagging + Elastic `assets` projection). Published assets are consumed by
> COMM, JRNY and SALE.
> EARS notation guide: `docs/architecture/backend/standards/ears-notation.md`.

## Purpose

Give the growth team one place to create, compose, version, approve and reuse content assets,
with provenance and human approval before publication. ASST operates exclusively in the tenant
schema `emp_<slug>` and never calls an AI provider directly — all AI capability is delegated to
TechLab AI over HTTP.

## Spec map

| SPEC | Theme | Status |
|---|---|---|
| [SPEC-01](spec/backend/SPEC-01-api-surface.md) | API surface (`/api/v1/assets/**`) | draft |
| [SPEC-02](spec/backend/SPEC-02-asset-lifecycle.md) | Asset lifecycle & approval (core orchestration) | draft |
| [SPEC-03](spec/backend/SPEC-03-asset-studio-composition.md) | Asset Studio (TechLab AI document_composition) | draft |
| [SPEC-04](spec/backend/SPEC-04-data-model-migrations.md) | Data model + migrations (`emp_<slug>`) | draft |
| [SPEC-05](spec/backend/SPEC-05-idempotency-concurrency.md) | Idempotency + concurrency | draft |
| [SPEC-06](spec/backend/SPEC-06-security.md) | Security (JWT, `asst.*` permissions, tenant guard) | draft |
| [SPEC-07](spec/backend/SPEC-07-observability-health.md) | Observability + health | draft |
| [SPEC-08](spec/backend/SPEC-08-bdd-test-scenarios.md) | BDD test scenarios | draft |
| [SPEC-09](spec/backend/SPEC-09-messaging-architecture.md) | Messaging (Kafka) + outbox | draft |
| [SPEC-10](spec/backend/SPEC-10-integrations.md) | Integrations (TechLab AI, Elastic, WRKS) | draft |

## Contracts

- `contracts/api-contract.md` — REST surface + ProblemDetail errors
- `contracts/data-model.md` — asset DDL (`-- schema: empresa`)
- `contracts/event-contracts.md` — produced/consumed events
- `contracts/hub-integration.md` — inter-service (WRKS, COMM/JRNY/SALE, MIG)
- `contracts/integration-contracts.md` — external systems (Elasticsearch)
- `contracts/techlab-ai-integration.md` — **`document_composition`** (Asset Studio + Asset Intelligence)

## Key references

- `docs/architecture/integrations/techlab-ai-integration.md` (BE ↔ TechLab AI)
- `docs/architecture/integrations/elastic-data-contract.md` (index `assets`)
- `docs/architecture/shared/multi-empresa.md`, `docs/architecture/shared/modelo-dados/empresa.md`
- `docs/architecture/shared/contratos/error-model.md`, `docs/architecture/shared/rbac/permissoes.md`
