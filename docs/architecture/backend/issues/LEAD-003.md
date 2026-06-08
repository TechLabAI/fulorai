# LEAD-003 -- API surface: controllers + DTO records + ProblemDetail advice

## Contexto
Superfície REST do `lead-service` (`/leads`, `/surveys`, `/qualification`, `/segments`) com DTOs
`record` e tratamento de erro RFC 7807.

## Spec de referencia
- SPEC-01-api-surface
- SPEC-06-security

## Escopo
- `api.controller`: `LeadController`, `SurveyController`, `QualificationController`, `SegmentController`.
- `api.dto`: requests/responses como `record` (captura, qualify, regra, segmento, breakdown do score).
- `api.exception`: `@RestControllerAdvice` → `ProblemDetail` com o catálogo de `error.code` da `api-contract.md`.
- Headers: `X-Correlation-Id` (gera se ausente); `empresa_id` via claim JWT.

## Resultado esperado
Endpoints respondem (ainda delegando a serviços stub), com contrato de erro consistente.

## Criterios de aceite
- [ ] Controllers mapeiam exatamente os paths/verbos da `api-contract.md`.
- [ ] Erros retornam `application/problem+json` com `error.code` estável.
- [ ] `api.*` não depende de `infrastructure.*` (ArchUnit RULE-04).
- [ ] Nenhuma entidade JPA retornada diretamente (apenas DTO records).

## Dependencias
- LEAD-002 (precede)

## Estimativa
M

## Prioridade
P1
