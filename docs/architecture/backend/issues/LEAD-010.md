# LEAD-010 -- TechLab AI qualification client + port (assist + fallback)

## Contexto
Cliente HTTP da capacidade `qualification` da TechLab AI, atrás de `TechLabQualificationPort`, com
Resilience4j (circuit breaker/timeout) e **fail-open** para o cálculo determinístico.

## Spec de referencia
- SPEC-03-maturity-score-6d
- SPEC-10-integrations
- (contracts) techlab-ai-integration.md

## Escopo
- `infrastructure.clients.TechLabAiClient` implementa `TechLabQualificationPort`.
- DTOs **gerados** de `integrations/techlab-ai/openapi.json` (openapi-generator-cli) — não escritos à mão.
- Resilience4j: timeout 1.5s, ≤1 retry, circuit breaker; fallback → score determinístico (`assist_ia=false`).
- Propaga `X-Correlation-Id`/`empresaId`/`principalId`; flag `LEAD_QUALIFICATION_ASSIST_ENABLED` (default false até P3 sync).

## Resultado esperado
Assist enriquece o score quando disponível; falha degrada sem quebrar a qualificação.

## Criterios de aceite
- [ ] Falha/timeout da TechLab AI → score determinístico, `assist_ia=false`, request 200.
- [ ] Cliente nunca chama provedor de IA direto (CLAUDE.md); só TechLab AI.
- [ ] `@FeignClient`/cliente HTTP apenas em `infrastructure.clients` (RULE-06).
- [ ] Flag desabilitada não chama a TechLab AI.

## Dependencias
- LEAD-006 (motor de score)
- INT-LEAD-003 (wiring/geração de DTO)

## Estimativa
M

## Prioridade
P4
