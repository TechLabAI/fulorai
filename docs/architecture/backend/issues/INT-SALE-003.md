# INT-SALE-003 — Integração Elasticsearch (revenue-events, campaign-events)

## Contexto
Validar a projeção fact de receita/campanha nos índices Elastic e a degradação graciosa.

## Spec de referencia
- `contracts/integration-contracts.md` §1, SPEC-10

## Escopo
Teste de indexação em `compra.confirmada`/`receita.atribuida`; índices `revenue-events`/
`campaign-events`; falha de Elastic não bloqueia a receita.

## Resultado esperado
Analytics de receita alimentado sem acoplar a transação.

## Criterios de aceite
- [ ] documentos projetados em `revenue-events`/`campaign-events`
- [ ] indisponibilidade do Elastic → retém transacional + retry (sem falhar request)

## Dependencias
- SALE-012 (precede)

## Estimativa
S

## Prioridade
P4
