# SPEC-01 — API Surface (INTL)

> Ref: `contracts/api-contract.md`. ADR-002, ADR-005. EARS: `standards/ears-notation.md`.

## Objetivo

Definir a superfície REST de `intl-service`: Copilot, Knowledge e Analytics, sob `/api/v1`,
autorizada por `intl.*` e isolada por `empresa`.

## Escopo

**In:** `/copilot/**`, `/knowledge/**`, `/analytics/**` (read-only), `/actuator/health`.
**Out:** UI; APIs de escrita em índices de *fact* de outros módulos; webhooks externos (pós-MVP).

## Decisões técnicas

- Tenant do claim JWT `empresa` (nunca de path/body) — ADR-004.
- AccessDecision por endpoint via `AccessEvaluateClient` — fail-closed.
- Falha de IA no copiloto **não** vira `5xx` (degrada) — ADR-005.

## Implementação

- `CopilotController`, `KnowledgeController`, `AnalyticsController` (api/controller).
- DTOs records em `api/dto`; `@RestControllerAdvice` → `ProblemDetail`.

## Casos de borda

- Conversa/nó inexistente na `empresa` → `404`.
- Indexação concorrente do mesmo nó → `409`.
- Embedding indisponível → `503` (sem caminho degradado).

## Critérios de aceite (EARS)

- THE SYSTEM SHALL expor `/api/v1/copilot`, `/api/v1/knowledge`, `/api/v1/analytics`.
- IF o JWT está ausente/inválido, THEN THE SYSTEM SHALL responder `401`.
- IF o AccessDecision nega `intl.*`, THEN THE SYSTEM SHALL responder `403`.
- WHEN qualquer endpoint é chamado, THE SYSTEM SHALL operar no schema `emp_<slug>` do claim `empresa`.
- THE SYSTEM SHALL retornar erros em formato RFC 7807 (`ProblemDetail`).
