# INT-LEAD-003 -- TechLab AI integration wiring (DTO generation + feature flag)

## Contexto
Infra de integração com a TechLab AI (capacidade `qualification`): geração de DTOs do OpenAPI,
configuração do cliente e flag de habilitação.

## Spec de referencia
- techlab-ai-integration.md
- integration-contracts.md
- SPEC-10-integrations

## Escopo
- Pipeline `openapi-generator-cli` gerando DTOs em `src/main/gen/techlabai/dtos/` de
  `integrations/techlab-ai/openapi.json`.
- Config do cliente (`TECHLAB_AI_BASE_URL`, `TECHLAB_AI_JWT_ENABLED`), Resilience4j, propagação de headers.
- Flag `LEAD_QUALIFICATION_ASSIST_ENABLED` (default false).
- **Bloqueado** enquanto o snapshot `integrations/techlab-ai/` estiver vazio (P3 `PENDING_FIRST_COMMIT`).

## Resultado esperado
Quando o sync P3 ocorrer, DTOs gerados e cliente pronto; até lá, assist desabilitado sem impactar o score determinístico.

## Criterios de aceite
- [ ] DTOs gerados do `openapi.json` (não escritos à mão; não editados).
- [ ] Flag desabilitada → score 100% determinístico.
- [ ] Wiring documentado; bloqueio P3 sinalizado.

## Dependencias
- LEAD-010 (cliente)
- (externo) P3 — sync TechLab AI

## Estimativa
S

## Prioridade
P4
