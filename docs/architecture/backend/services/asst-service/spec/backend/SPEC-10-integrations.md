# SPEC-10 — Integrations

> Contratos: `contracts/{techlab-ai-integration,integration-contracts,hub-integration}.md`. EARS guide linkado.

## Objetivo

Especificar as integrações de `asst-service`: TechLab AI (`document_composition`),
Elasticsearch (`assets`) e WRKS (AccessDecision), com resiliência e fallback.

## Escopo

- **In:** cliente TechLab AI (resiliente), adapter Elastic (`assets`), Feign WRKS, propagação de headers, geração de DTOs.
- **Out:** modelos/prompts da IA; entrega de mensagens (COMM); object storage (out of MVP).

## Decisões técnicas

- **TechLab AI:** `TechLabAiClient` em `infrastructure/clients`; DTOs gerados de `openapi.json` (`gen/techlabai/`); Resilience4j; fallback graceful (ADR-003). Nunca chamar provider direto.
- **Elasticsearch:** `AssetSearchAdapter` (direct java client); upsert best-effort; filtro por `empresaId`; reindex reconciliável.
- **WRKS:** `AccessEvaluateClient` (Feign) + validação JWKS; cache de AccessDecision.

## Casos de borda

- TechLab AI/openapi placeholder (P3) → coupling point marcado; DTOs gerados quando o SHA for pinado.
- Elastic indisponível → write path intacto; busca cai para PostgreSQL.
- WRKS indisponível com cache válido → serve do cache.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL call TechLab AI only through TechLabAiClient and SHALL NOT call any AI provider directly.`
- `THE SYSTEM SHALL generate TechLab AI DTOs from integrations/techlab-ai/openapi.json and SHALL NOT hand-edit them.`
- `IF Elasticsearch is unavailable, THEN THE SYSTEM SHALL keep the PostgreSQL write path working and reconcile the index later.`
- `WHEN indexing an asset, THE SYSTEM SHALL tag the document with empresaId and SHALL filter all queries by the caller's tenant.`
- `THE SYSTEM SHALL propagate X-Correlation-Id to TechLab AI and Elasticsearch calls.`
- `THE SYSTEM SHALL store binaries as external URL references and SHALL NOT upload or transcode binary content in the MVP.`
