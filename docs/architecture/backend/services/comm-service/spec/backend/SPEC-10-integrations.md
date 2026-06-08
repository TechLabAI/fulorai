# SPEC-10 — Integrations (TechLab AI, channel providers, ASST, Elastic, WRKS)

> EARS guide linkado. Fonte: `contracts/{techlab-ai-integration,integration-contracts,hub-integration}.md`. ADR-003, ADR-005.

## Objetivo

Especificar as integrações externas e inter-serviço de COMM e suas políticas de resiliência:
TechLab AI (Template Studio), provedores de canal (adapters), ASST (assets), Elastic
(`communication-events`) e WRKS (AccessDecision).

## Escopo

- **In:** cliente TechLab AI (`document_composition`); adapters de canal sob `CanalEnvioPort`; `AssetQueryClient` (ASST); projeção Elastic; `AccessEvaluateClient` (WRKS); resiliência (timeout/CB/retry/fallback).
- **Out:** detalhes da máquina de entrega (SPEC-02); modelo RBAC (SPEC-06).

## Decisões técnicas

- **TechLab AI:** `TechLabAiClient` (HTTP, DTOs gerados de `openapi.json`), `document_composition`, timeout 20s + CB 50%; falha → `503 comm.studio.ia-indisponivel`, sem alterar template (degradação graciosa).
- **Provedores de canal:** um adapter por canal/provedor (ADR-005); Resilience4j por adapter; credenciais via `config_canal.credencial_ref`; normalização de webhook → `EventoEntrega`.
- **ASST:** `AssetQueryClient` `@FeignClient(name="asst-service")` lê só assets **publicados**; ASST fora → corpo embutido/cache (best-effort).
- **Elastic:** projeção `communication-events` (fact) best-effort; falha não bloqueia disparo; reconciliável de `evento_entrega`.
- **WRKS:** `AccessEvaluateClient` + JWKS; cache de AccessDecision com fallback.

## Casos de borda

- TechLab AI timeout no Studio → `503`, template inalterado.
- Provedor 429 → backoff no worker, sem falhar request.
- Provedor down após retries → `FALHADA` + `journey-os.mensagem.falhada` + DLQ.
- ASST indisponível ao compor com `assetOrigemId` → segue com aviso de fonte degradada.
- Elastic down → indexação pulada, reconciliada depois.

## Critérios de aceite (EARS)

- `WHEN the Template Studio calls document_composition AND it returns within the timeout, THE SYSTEM SHALL store the composed body in RASCUNHO with briefComposicao recorded.`
- `IF document_composition fails/times out/circuit-open, THEN THE SYSTEM SHALL respond 503 'comm.studio.ia-indisponivel' AND SHALL NOT change the template.`
- `WHEN the dispatch worker sends, THE SYSTEM SHALL select the channel adapter by (canal, provedor) and call the provider under Resilience4j.`
- `IF a channel provider fails after the configured retries, THEN THE SYSTEM SHALL mark the message FALHADA and route the job to the DLQ.`
- `WHERE a template references a published asset, THE SYSTEM SHALL read it via AssetQueryClient and SHALL never read draft/rejected versions.`
- `WHEN a delivery event is recorded, THE SYSTEM SHALL index it into communication-events best-effort AND SHALL NOT fail the dispatch path if Elastic is unavailable.`
- `THE SYSTEM SHALL never call an AI provider directly — all AI capability goes through TechLab AI over HTTP.`
