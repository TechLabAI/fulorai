---
service: comm-service
module: COMM
type: standard
package: com.journeyos.comm
gradleKey: ":services:comm-service"
port: 8085
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
  - adr/ADR-005-channel-adapter-pattern.md
---

# COMM — Communication Hub Spec (comm-service)

> **Full spec set.** COMM is the **communication hub**: the single place a workspace standardizes
> message **templates** (with AI-assisted composition delegated to TechLab AI
> `document_composition`), routes messages by rule, **dispatches** them across WhatsApp/Email/
> Telegram/SMS through provider-agnostic **channel adapters**, and tracks the full **delivery
> lifecycle**. COMM operates exclusively in the tenant schema `emp_<slug>` and never calls an AI
> provider directly. JRNY/SALE/LEAD trigger sends; ASST supplies published assets as template source.
> EARS notation guide: `docs/architecture/backend/standards/ears-notation.md`.

## Purpose

Give growth and SDR teams one place to talk to leads/clients: versioned templates, explicit
routing (channel + fallback), idempotent dispatch, and a trustworthy delivery trail
(enqueued → sent → delivered → read / failed). Providers (Meta/Twilio/SES/Telegram) live behind a
single outbound port (`CanalEnvioPort`); the domain knows only `canal`.

## Spec map

| SPEC | Theme | Status |
|---|---|---|
| [SPEC-01](spec/backend/SPEC-01-api-surface.md) | API surface (`/api/v1/templates|messages|routing-rules|channels|webhooks`) | draft |
| [SPEC-02](spec/backend/SPEC-02-message-dispatch-lifecycle.md) | Message dispatch & delivery state machine (core orchestration) | draft |
| [SPEC-03](spec/backend/SPEC-03-channel-routing.md) | Channel routing & adapter pattern (sub-feature) | draft |
| [SPEC-04](spec/backend/SPEC-04-data-model-migrations.md) | Data model + migrations (`emp_<slug>`) | draft |
| [SPEC-05](spec/backend/SPEC-05-idempotency-concurrency.md) | Idempotency + concurrency | draft |
| [SPEC-06](spec/backend/SPEC-06-security.md) | Security (JWT, `comm.*` permissions, webhook signature, tenant guard) | draft |
| [SPEC-07](spec/backend/SPEC-07-observability-health.md) | Observability + health | draft |
| [SPEC-08](spec/backend/SPEC-08-bdd-test-scenarios.md) | BDD test scenarios | draft |
| [SPEC-09](spec/backend/SPEC-09-messaging-architecture.md) | Messaging (Kafka) + outbox + dispatch worker | draft |
| [SPEC-10](spec/backend/SPEC-10-integrations.md) | Integrations (TechLab AI, channel providers, ASST, Elastic, WRKS) | draft |

## Contracts

- `contracts/api-contract.md` — REST surface + ProblemDetail errors
- `contracts/data-model.md` — communication DDL (`-- schema: empresa`)
- `contracts/event-contracts.md` — produced/consumed events
- `contracts/hub-integration.md` — inter-service (WRKS, ASST, JRNY/SALE/LEAD, MIG)
- `contracts/integration-contracts.md` — external systems (channel providers, Elasticsearch)
- `contracts/techlab-ai-integration.md` — **`document_composition`** (Template Studio)

## Key references

- `docs/architecture/integrations/techlab-ai-integration.md` (BE ↔ TechLab AI)
- `docs/architecture/integrations/elastic-data-contract.md` (index `communication-events`)
- `docs/architecture/shared/multi-empresa.md`, `docs/architecture/shared/modelo-dados/empresa.md`
- `docs/architecture/shared/contratos/error-model.md`, `docs/architecture/shared/rbac/permissoes.md`
- `docs/architecture/backend/services/asst-service/contracts/hub-integration.md` (`AssetQueryClient`)
