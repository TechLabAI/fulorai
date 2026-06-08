# INT-SALE-002 — Integração LEAD (lead.qualificado → oportunidade)

## Contexto
Validar o consumo dos eventos de LEAD que criam/priorizam oportunidades.

## Spec de referencia
- `contracts/hub-integration.md` §1, `contracts/event-contracts.md` §2, SPEC-09

## Escopo
Teste de consumo de `journey-os.lead.qualificado` e `journey-os.lead.score.atualizado`; idempotência
por `leadId`; tolerância a fora de ordem.

## Resultado esperado
Golden path automático lead→oportunidade.

## Criterios de aceite
- [ ] `lead.qualificado` cria oportunidade (idempotente; sem duplicar)
- [ ] `lead.score.atualizado` antes de `qualificado` é no-op tolerado
- [ ] contexto de tenant estabelecido do header

## Dependencias
- SALE-016 (precede)

## Estimativa
M

## Prioridade
P6
