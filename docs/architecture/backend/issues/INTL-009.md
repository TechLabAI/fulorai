# INTL-009 -- TechLab AI client (knowledge + orchestration)

## Contexto
Implementar o cliente HTTP da TechLab AI com resiliência e fallback.

## Spec de referência
- SPEC-10, `contracts/techlab-ai-integration.md`

## Escopo
`TechLabAiClient` implementando `KnowledgePort` (embed/retrieve) e `OrchestrationPort` (compose).
Resilience4j (CB + timeout). Fallback: copilot → recuperação-apenas; embedding → `503`. DTOs
gerados de `openapi.json` (placeholder até P3 sync). Nunca IA direta.

## Resultado esperado
Composição fundamentada quando disponível; degradação controlada quando não.

## Critérios de aceite
- [ ] CB abre após threshold e dispara fallback recuperação-apenas
- [ ] `embed` falho na indexação → `503` (sem indexar parcial)
- [ ] Registra `modelo`/`custoTokens`/`latenciaMs`
- [ ] Headers de propagação (correlation/tenant/principal) enviados

## Dependências
- INTL-001 (precede); INT-INTL-002 (contrato)

## Estimativa
L

## Prioridade
P4
