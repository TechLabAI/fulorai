---
service: intl-service
module: INTL
type: standard
package: com.journeyos.intl
gradleKey: ":services:intl-service"
port: 8087
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
  - adr/ADR-003-event-platform-indexing-strategy.md
  - adr/ADR-004-multitenant-strategy.md
  - adr/ADR-005-ai-copilot-integration.md
---

# INTL — Intelligence & Platform Spec (intl-service)

> **Full spec set.** INTL é a **camada de inteligência e plataforma** do Journey OS: um **AI Copilot**
> conversacional que responde perguntas **fundamentadas e citadas** sobre os dados da `empresa`
> (RAG: recuperação no Elasticsearch → composição via TechLab AI `knowledge`/`orchestration`), uma
> **Base de Conhecimento** curada, a **governança da plataforma de dados Elastic** (contrato de
> rastreabilidade D-269, DLQ, registro de índices/ILM) e uma **leitura analítica cross-index**.
> INTL opera no schema `emp_<slug>` (PG) + índices compartilhados (Elastic, discriminador `empresa`),
> **não** reindexа os *facts* de outros módulos (ADR-003) e **nunca** chama IA direto (sempre TechLab AI).
> EARS guide: `docs/architecture/backend/standards/ears-notation.md`.

## Purpose

Transformar dados dispersos em **respostas auditáveis** e **analítica consolidada** confiável, sem
"IA caixa-preta": toda resposta cita evidência verificável; degradação graciosa quando a IA falha;
isolamento de tenant inviolável.

## Spec map

| SPEC | Tema |
|---|---|
| SPEC-01 | API surface (`/copilot`, `/knowledge`, `/analytics`) |
| SPEC-02 | Copilot orchestration (RAG fundamentado) |
| SPEC-03 | Knowledge base & event platform (ingestão, projeção, governança) |
| SPEC-04 | Data model + migrations |
| SPEC-05 | Idempotency + concurrency |
| SPEC-06 | Security (OAuth2, multi-tenancy, LGPD) |
| SPEC-07 | Observability + health |
| SPEC-08 | BDD test scenarios |
| SPEC-09 | Messaging architecture |
| SPEC-10 | Integrations (TechLab AI, Elasticsearch, WRKS, ASST) |

## Contracts

- `contracts/api-contract.md` · `contracts/data-model.md` · `contracts/event-contracts.md`
- `contracts/techlab-ai-integration.md` · `contracts/hub-integration.md` · `contracts/integration-contracts.md`

## Domain anchor

`journey-os.copilot.resposta.gerada` — "Copiloto respondeu".
