# SALE-016 — Consumers de eventos (LEAD + WRKS) idempotentes

## Contexto
Consumir `lead.qualificado`/`lead.score.atualizado` (cria/prioriza oportunidade) e
`empresa.provisionada`/`modelo.acesso.alterado` (seed/cache) de forma idempotente.

## Spec de referencia
- SPEC-09, `contracts/event-contracts.md` §2

## Escopo
Consumers em `infrastructure.messaging.consumer`; estabelecer `EmpresaContextHolder` do header;
idempotência por `(correlationId, evento)` e por `leadId` (uma oportunidade aberta por lead);
seed de pipeline/ofertas/modelo default em `empresa.provisionada`.

## Resultado esperado
Criação reativa de oportunidade + seed por tenant.

## Criterios de aceite
- [ ] `lead.qualificado` cria/atualiza oportunidade sem duplicar (idempotente por `leadId`)
- [ ] `empresa.provisionada` faz seed idempotente (estágios/ofertas/modelo LAST_TOUCH)
- [ ] evento repetido `(correlationId,evento)` é ignorado
- [ ] `EmpresaContextHolder.clear()` no `finally`

## Dependencias
- SALE-005, SALE-015 (precede)

## Estimativa
M

## Prioridade
P6
