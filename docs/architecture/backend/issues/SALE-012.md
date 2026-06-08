# SALE-012 — Adapter Elasticsearch (revenue-events, campaign-events)

## Contexto
Projetar eventos de receita e campanha nos índices fact `revenue-events` e `campaign-events` para
funil/ROI; consultas de funil.

## Spec de referencia
- SPEC-10, `contracts/integration-contracts.md` §1

## Escopo
`SaleSearchPort` + adapter Elastic (`direct-java-client`). Indexação best-effort em
`compra.confirmada`/`receita.atribuida`; não bloqueia a receita.

## Resultado esperado
Receita/atribuição indexadas para analytics.

## Criterios de aceite
- [ ] indexa `revenue-events`/`campaign-events` de forma assíncrona
- [ ] falha do Elastic não derruba a requisição (retém transacional, retry)
- [ ] adapter implementa `SaleSearchPort`

## Dependencias
- SALE-006, SALE-007 (precede)

## Estimativa
M

## Prioridade
P4
