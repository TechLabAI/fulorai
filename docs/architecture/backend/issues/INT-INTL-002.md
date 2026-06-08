# INT-INTL-002 -- Integração TechLab AI (knowledge + orchestration)

## Contexto
RAG do copiloto e embeddings dependem da TechLab AI (HTTP). DTOs gerados de `openapi.json`.

## Spec de referência
- SPEC-10, `contracts/techlab-ai-integration.md`, `integration-contracts.md`

## Escopo
Operações `embed`/`retrieve`/`compose`; Resilience4j (CB/timeout); fallback recuperação-apenas;
headers de propagação; geração de DTOs via `openapi-generator-cli`. **Bloqueado** pelo sync P3
(`openapi.json` vazio) — programar contra as portas até o sync.

## Resultado esperado
Composição fundamentada com fallback robusto.

## Critérios de aceite
- [ ] Porta `KnowledgePort`/`OrchestrationPort` implementada
- [ ] CB + fallback verificados (copilot degrada, embedding `503`)
- [ ] DTOs gerados após o sync; nunca IA direta

## Dependências
- INTL-009 · **Bloqueado por:** P3 (TechLab AI sync)

## Estimativa
L

## Prioridade
P4
