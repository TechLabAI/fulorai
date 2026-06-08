# SPEC-03 — Asset Studio (TechLab AI document_composition)

> Sub-feature crítica. Contrato: `contracts/techlab-ai-integration.md`. ADR-003. EARS guide linkado.

## Objetivo

Especificar a composição/edição de conteúdo assistida por IA, delegada à TechLab AI
`document_composition`, produzindo uma nova versão imutável em `RASCUNHO`.

## Escopo

- **In:** orquestração da chamada à TechLab AI, persistência do resultado como `versao_asset` (origem=ASSET_STUDIO), proveniência (brief), resiliência e idempotência.
- **Out:** modelos/prompts/providers (responsabilidade da TechLab AI); publicação automática (proibida).

## Decisões técnicas

- `ComporNoStudioService` (application) usa `ComposicaoIaPort` (out) → `TechLabAiClient` (infra/clients).
- **Nunca** chamar provider de IA direto (regra do monorepo). DTOs gerados de `openapi.json`.
- Resilience4j (timeout + circuit breaker); fallback graceful (ADR-003).
- Idempotência via `Idempotency-Key` (SPEC-05).

## Implementação

1. Valida permissão `asst.studio.compor` + estado do asset (não bloqueante a CRUD).
2. Monta `BriefComposicao` (brief + contexto da empresa + base opcional).
3. Chama TechLab AI; em sucesso, cria `versao_asset` (RASCUNHO, origem=ASSET_STUDIO, `brief_composicao` gravado).
4. Dispara Asset Intelligence (tags IA) best-effort.

## Casos de borda

- TechLab AI timeout/erro/circuito aberto → 503, nenhuma versão criada.
- Replay de `Idempotency-Key` → retorna versão já produzida, sem nova chamada à IA.
- Composição sobre asset publicado → cria nova versão RASCUNHO (numero+1), não altera a vigente.

## Critérios de aceite (EARS)

- `WHEN a composition succeeds within the timeout, THE SYSTEM SHALL persist a new versao_asset with origem=ASSET_STUDIO in state RASCUNHO and record brief_composicao.`
- `THE SYSTEM SHALL never publish an Asset-Studio-produced version automatically.`
- `IF TechLab AI is unavailable, times out, or the circuit is open, THEN THE SYSTEM SHALL respond 503 error.code 'asst.studio.ia-indisponivel' AND SHALL NOT create a version.`
- `IF the same Idempotency-Key is replayed, THEN THE SYSTEM SHALL return the previously produced version without calling TechLab AI again.`
- `WHILE TechLab AI is degraded, THE SYSTEM SHALL keep CRUD, versioning, approval and publication fully operational.`
- `WHERE Asset Intelligence returns tag suggestions, THE SYSTEM SHALL persist them with origem=IA without blocking the composition response.`
