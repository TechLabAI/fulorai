# SPEC-10 — Integrations

> Ref: `contracts/techlab-ai-integration.md`, `contracts/integration-contracts.md`,
> `contracts/hub-integration.md`. ADR-005, ADR-003.

## Objetivo

Especificar as integrações externas de INTL e suas políticas de resiliência.

## Escopo

**In:** TechLab AI (`knowledge`/`orchestration`); Elasticsearch (`elastic-client-lib`); WRKS
(AccessDecision/JWKS + eventos); ASST (`AssetQueryClient` + evento); Kafka.
**Out:** Integration Hub externo / webhooks de 3º (pós-MVP); ingestão de observabilidade (infra).

## Decisões técnicas

- **TechLab AI:** `TechLabAiClient` (HTTP, DTOs gerados de `openapi.json`); Resilience4j (CB +
  timeout); fallback recuperação-apenas. Nunca IA direta.
- **Elasticsearch:** `SearchPort`/`IndexPort` do `elastic-client-lib`; bloco de rastreabilidade +
  DLQ; filtro `empresa` obrigatório.
- **WRKS:** `AccessEvaluateClient` Feign + JWKS; consumo de eventos de tenant.
- **ASST:** `AssetQueryClient` Feign (opcional) + consumo de `asset.versao.publicada`.

## Matriz de fallback

| Dependência | Falha → | Comportamento |
|---|---|---|
| TechLab AI | copilot `DEGRADADA` / embedding `503` | degrada / retry |
| Elasticsearch (read) | copilot `NAO_FUNDAMENTADA` / analytics `503` | sem evidência |
| Elasticsearch (write) | projeção → DLQ + retry | auditoria atrasada |
| WRKS AccessDecision | `403`/`503` (fail-closed) | bloqueia operação |
| ASST | ingestão adiada | nó pendente de conteúdo |

## Critérios de aceite (EARS)

- THE SYSTEM SHALL consumir TechLab AI exclusivamente via `TechLabAiClient` (sem IA direta).
- IF a TechLab AI está indisponível no copiloto, THEN THE SYSTEM SHALL degradar (recuperação-apenas) sem `5xx`.
- THE SYSTEM SHALL projetar todo documento via `IndexPort` com o bloco de rastreabilidade; violação → DLQ.
- THE SYSTEM SHALL autorizar via `AccessEvaluateClient` antes de executar operação `intl.*` (fail-closed).
- WHERE o evento de asset não traz o conteúdo completo, THE SYSTEM SHALL buscá-lo via `AssetQueryClient`.
