# INT-ASST-003 -- TechLab AI document_composition (cliente HTTP + Resilience4j + DTO gen)

## Contexto
Cliente HTTP resiliente para a capacidade `document_composition` da TechLab AI, base do Asset
Studio. Nunca chamar provider de IA direto.

## Spec de referencia
- contracts/techlab-ai-integration.md
- SPEC-03-asset-studio-composition

## Escopo
- `TechLabAiClient` em `infrastructure/clients` (HTTP); DTOs gerados de `integrations/techlab-ai/openapi.json` (`gen/techlabai/`).
- Resilience4j: timeout (`TECHLAB_AI_TIMEOUT_MS`), circuit breaker (`TECHLAB_AI_CB_FAILURE_RATE`).
- Propagação de `X-Correlation-Id` + tenant/principal; fallback graceful.
- **Bloqueio conhecido:** `openapi.json` é placeholder (P3); coupling point marcado até o SHA ser pinado.

## Resultado esperado
Asset Studio chama TechLab AI com resiliência; IA fora → 503 sem afetar CRUD.

## Criterios de aceite
- [ ] DTOs gerados de `openapi.json` (não hand-written) quando o SHA for pinado.
- [ ] Timeout/circuit breaker configurados; fallback graceful.
- [ ] `X-Correlation-Id` propagado.
- [ ] Nenhuma chamada direta a provider de IA (RULE do monorepo).

## Dependencias
- TechLab AI (P3 — placeholder); ASST-009

## Estimativa
M

## Prioridade
P4
