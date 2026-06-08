# SPEC-10 — Integrations

> Contratos: `contracts/{techlab-ai-integration,integration-contracts,hub-integration}.md`.
> ADR-003 (assist resiliente), ADR-005 (determinístico primeiro). EARS guide:
> `docs/architecture/backend/standards/ears-notation.md`.

## Objetivo

Especificar as integrações de `jrny-service`: TechLab AI (`orchestration`, opcional),
Elasticsearch (`journey-events`/`routing-decisions`), ASST (`AssetQueryClient`) e WRKS
(AccessDecision), com resiliência e fallback determinístico.

## Escopo

- **In:** cliente TechLab AI (resiliente, opcional), adapters Elastic (fact), Feign ASST/WRKS, propagação de headers, geração de DTOs.
- **Out:** modelos/prompts da IA; execução de mensagem (COMM); criação de oportunidade (SALE).

## Decisões técnicas

- **TechLab AI:** `TechLabAiClient` em `infrastructure/clients` (não `@FeignClient`); DTOs gerados de `openapi.json` (`gen/techlabai/`); Resilience4j (timeout curto + CB); **fallback determinístico** (ADR-003/ADR-005). Nunca chamar provider direto. Implementa `RecomendacaoIaPort`.
- **Elasticsearch:** `JourneyEventIndexAdapter` (direct java client) → `journey-events` (transições) e `routing-decisions` (decision log); upsert best-effort; filtro por `empresaId`; reindex reconciliável.
- **ASST:** `AssetQueryClient` (Feign) → conteúdo publicado de estágio; refresh reativo por `asset.versao.publicada`.
- **WRKS:** `AccessEvaluateClient` (Feign) + validação JWKS; cache de AccessDecision.

## Casos de borda

- TechLab AI/openapi placeholder (P3) → coupling point marcado (`RecomendacaoIaPort`); DTOs gerados quando o SHA for pinado.
- TechLab AI indisponível/timeout → fallback determinístico; `assist_ia=INDISPONIVEL`; decisão não bloqueia.
- Elastic indisponível → decisão intacta; projeção reconciliada depois.
- ASST indisponível → usa última referência conhecida de conteúdo; não bloqueia roteamento.
- WRKS indisponível com cache válido → serve do cache.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL call TechLab AI only through TechLabAiClient and SHALL NOT call any AI provider directly.`
- `THE SYSTEM SHALL generate TechLab AI DTOs from integrations/techlab-ai/openapi.json and SHALL NOT hand-edit them.`
- `IF TechLab AI orchestration is unavailable, times out, or the circuit is open, THEN THE SYSTEM SHALL fall back to deterministic routing and record assist_ia=INDISPONIVEL, never blocking the decision.`
- `WHEN a routing decision or a stage transition is persisted, THE SYSTEM SHALL index it into routing-decisions / journey-events best-effort, tagged with empresaId, and SHALL filter every query by the caller's tenant.`
- `IF Elasticsearch is unavailable, THEN THE SYSTEM SHALL keep the routing decision committed in PostgreSQL and reconcile the index later.`
- `WHEN a stage references a published asset, THE SYSTEM SHALL resolve it via AssetQueryClient and SHALL expose only published versions.`
- `IF ASST is unreachable, THEN THE SYSTEM SHALL serve the last-known stage content reference and SHALL NOT fail routing.`
- `THE SYSTEM SHALL propagate X-Correlation-Id to TechLab AI, ASST, WRKS and Elasticsearch calls.`
