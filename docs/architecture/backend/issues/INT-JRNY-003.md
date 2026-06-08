# INT-JRNY-003 -- Contrato TechLab AI orchestration (DTOs gerados de openapi.json) — coupling point

## Contexto
Acoplamento fino do assist de roteamento à TechLab AI (`orchestration`). DTOs **gerados** de
`integrations/techlab-ai/openapi.json` (não hand-written). Ponto de coupling marcado — o
`openapi.json` é placeholder até o SHA upstream ser pinado (P3 bloqueado).

## Spec de referencia
- techlab-ai-integration.md
- integration-contracts.md
- SPEC-10-integrations

## Escopo
- Geração de DTOs via `openapi-generator-cli` em `backend/services/jrny-service/src/main/gen/techlabai/dtos/`.
- Cliente HTTP `orchestration` em `infrastructure/clients` (não-Feign); headers `correlationId`/`tenantId`/`principalId`.
- Mapeamento request (contexto lead+jornada) ↔ `RecomendacaoIa` de domínio.
- Marcar o ponto exato de coupling; degradar quando o contrato/serviço não estiver disponível.

## Resultado esperado
Quando o SHA do TechLab AI for pinado, os DTOs regeneram e o assist funciona; até lá, o caminho determinístico é o padrão.

## Criterios de aceite
- [ ] DTOs gerados de `openapi.json` (nunca editados à mão).
- [ ] Cliente isola o contrato; troca de SHA não toca o domínio.
- [ ] Contrato ausente/placeholder não quebra o build do roteamento determinístico.

## Dependencias
- JRNY-009 (consumidor do port)

## Estimativa
M

## Prioridade
P4
