# SALE-008 — LtvCalculator (LTV determinístico por contato)

## Contexto
Domain service POJO que recalcula o LTV materializado de um `contato_ref` como soma determinística
das compras `CONFIRMADA`.

## Spec de referencia
- SPEC-03, `contracts/data-model.md` §3.9

## Escopo
`LtvCalculator` (domain) + `LtvService` (findByContato/listAll). Recálculo em
`compra.confirmada`/estorno/cancelamento; exclui `ESTORNADA`/`CANCELADA`. Publica
`journey-os.ltv.atualizado`.

## Resultado esperado
LTV consultável e determinístico.

## Criterios de aceite
- [ ] LTV = soma das compras CONFIRMADA do contato (determinístico)
- [ ] estorno/cancelamento recalcula e exclui do total
- [ ] `GET /ltv/{contatoRef}` e listagem por valor desc
- [ ] publica `journey-os.ltv.atualizado`

## Dependencias
- SALE-006 (precede)

## Estimativa
M

## Prioridade
P2
