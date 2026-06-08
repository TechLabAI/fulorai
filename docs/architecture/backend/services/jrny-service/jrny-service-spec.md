---
service: jrny-service
module: JRNY
type: standard
package: com.journeyos.jrny
gradleKey: ":services:jrny-service"
port: 8084
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
  - adr/ADR-005-routing-engine-model.md
---

# JRNY — Journey & Routing Spec (jrny-service)

> **Full spec set.** JRNY is the **journey & routing engine**: it owns the multi-stage journey
> design (**Journey Builder**), the decision of **where each lead goes next** (**Routing
> Engine** — deterministic versioned rules, optionally assisted by TechLab AI `orchestration`)
> and the immutable **decision log** (`decisao_roteamento`). JRNY **decides and signals**; it
> never executes channel/sales actions — COMM and SALE react to its events. It operates
> exclusively in the tenant schema `emp_<slug>` and never calls an AI provider directly.
> EARS notation guide: `docs/architecture/backend/standards/ears-notation.md`.

## Purpose

Transformar o sinal de qualificação produzido por LEAD em movimento estruturado pelo funil
(captura → nutrição → qualificação → oferta → fechamento → pós-venda), de forma determinística,
versionada e auditável. Marina (HEAD_GROWTH) desenha jornadas e regras; Rafael (INFOPRODUTOR)
publica; Lucas (SDR) lê o estado e o "por quê". A cada evento de domínio, o Routing Engine decide
o estágio-alvo do lead, matricula/avança a `inscricao_jornada`, grava uma `decisao_roteamento`
imutável e emite `journey-os.lead.roteado` (evento-âncora) para COMM/SALE agirem. A inteligência
de recomendação é **delegada à TechLab AI** (`orchestration`) e é **sempre opcional**: o caminho
determinístico decide sozinho em falha/timeout.

## Spec map

| SPEC | Theme | Status |
|---|---|---|
| [SPEC-01](spec/backend/SPEC-01-api-surface.md) | API surface (`/api/v1/journeys/**`, `/api/v1/routing/**`) | draft |
| [SPEC-02](spec/backend/SPEC-02-routing-engine-orchestration.md) | Routing Engine & orchestration (core — anchor `lead.roteado`) | draft |
| [SPEC-03](spec/backend/SPEC-03-journey-builder.md) | Journey Builder (definition + versioning state machine) | draft |
| [SPEC-04](spec/backend/SPEC-04-data-model-migrations.md) | Data model + migrations (`emp_<slug>`) | draft |
| [SPEC-05](spec/backend/SPEC-05-idempotency-concurrency.md) | Idempotency + concurrency | draft |
| [SPEC-06](spec/backend/SPEC-06-security.md) | Security (JWT, `jrny.*` permissions, tenant guard) | draft |
| [SPEC-07](spec/backend/SPEC-07-observability-health.md) | Observability + health | draft |
| [SPEC-08](spec/backend/SPEC-08-bdd-test-scenarios.md) | BDD test scenarios | draft |
| [SPEC-09](spec/backend/SPEC-09-messaging-architecture.md) | Messaging (Kafka) + outbox | draft |
| [SPEC-10](spec/backend/SPEC-10-integrations.md) | Integrations (TechLab AI, ASST, WRKS, Elastic) | draft |

## Contracts

- `contracts/api-contract.md` — REST surface (`journeys` + `routing`) + ProblemDetail errors
- `contracts/data-model.md` — journey/stage/rule/enrolment/decision DDL (`-- schema: empresa`)
- `contracts/event-contracts.md` — produced/consumed events
- `contracts/hub-integration.md` — inter-service (WRKS, ASST, LEAD, COMM/SALE, MIG)
- `contracts/integration-contracts.md` — external systems (Elasticsearch `journey-events`/`routing-decisions`)
- `contracts/techlab-ai-integration.md` — **`orchestration`** (optional routing assist + deterministic fallback)

## Domain at a glance

| Aggregate / entity | Role |
|---|---|
| `jornada` (root) | Versioned multi-stage funnel definition; state machine `RASCUNHO → PUBLICADA → ARQUIVADA`. |
| `estagio` | Ordered, typed stage (`CAPTURA`..`POS_VENDA`); optional `asset_ref_id`; `terminal`; `config` jsonb. |
| `regra_roteamento` | Versioned predicate (`condicao` over score/dimension/segment/attribute) → target stage; `prioridade`. |
| `inscricao_jornada` | Lead's execution state in a journey (`ATIVA`/`CONCLUIDA`/`ENCERRADA`); pins the entry `jornada_versao`. |
| `decisao_roteamento` | **Immutable** decision log: trigger, input snapshot, fired rule, AI-assist flag, result, target. |

## Key references

- `docs/architecture/integrations/techlab-ai-integration.md` (BE ↔ TechLab AI, `orchestration`)
- `docs/architecture/integrations/elastic-data-contract.md` (indices `journey-events`, `routing-decisions`)
- `docs/architecture/shared/multi-empresa.md`, `docs/architecture/shared/modelo-dados/empresa.md`
- `docs/architecture/shared/contratos/error-model.md`, `docs/architecture/shared/rbac/permissoes.md`
- LEAD event payloads (`lead.qualificado`/`score.atualizado`/`segmento.alterado`): `../lead-service/contracts/event-contracts.md`
