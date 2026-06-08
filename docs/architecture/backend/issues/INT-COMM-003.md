# INT-COMM-003 -- TechLab AI client (document_composition) + Resilience4j

## Contexto
Cliente HTTP para a capability `document_composition` da TechLab AI (Template Studio), com DTOs
gerados de `openapi.json`.

## Spec de referencia
- techlab-ai-integration.md
- SPEC-10-integrations

## Escopo
- `TechLabAiClient` em `infrastructure.clients` (HTTP; DTOs gerados por `openapi-generator-cli` em `gen/techlabai/`).
- Implementa `ComposicaoIaPort`; timeout 20s + CB 50%; sem retry de composição (evita duplicação).
- Propaga `X-Correlation-Id` + tenant/principal; auth via `TECHLAB_AI_JWT_ENABLED`.
- **Bloqueado por P3** (sync upstream do `openapi.json` — placeholder até SHA pinado).

## Resultado esperado
Template Studio chama a IA via contrato gerado; degradação graciosa em falha.

## Criterios de aceite
- [ ] Composição via `ComposicaoIaPort` mapeada para corpo de template.
- [ ] Falha/timeout/CB aberto → 503 `comm.studio.ia-indisponivel`.
- [ ] DTOs gerados (não hand-written) em `gen/techlabai/`.

## Dependencias
- COMM-009 (relaciona)

## Estimativa
M

## Prioridade
P4
