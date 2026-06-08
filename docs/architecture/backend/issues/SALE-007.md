# SALE-007 — AttributionEngine (atribuição de receita determinística)

## Contexto
Domain service POJO que distribui a receita de uma compra entre touchpoints segundo o
`modelo_atribuicao` ativo (last/first/linear-touch), garantindo conservação de receita.

## Spec de referencia
- SPEC-03, ADR-005, `contracts/data-model.md` §3.6/§3.7

## Escopo
`AttributionEngine` (domain): estratégias LAST_TOUCH/FIRST_TOUCH/LINEAR; persistência de
`atribuicao` (breakdown) com `versao_modelo`; endpoints `/atribuicao/modelos` (+ activate),
`GET /compras/{id}/atribuicao`. Re-atribuição em ativação de modelo (lote pequeno síncrono).

## Resultado esperado
Receita atribuída e explicável por touchpoint.

## Criterios de aceite
- [ ] Σ `valor_atribuido` por compra = `compra.valor_total` (conservação)
- [ ] LAST_TOUCH credita o último touchpoint; LINEAR divide igualmente (resto no 1º)
- [ ] ativar modelo desativa o anterior atomicamente e re-atribui afetadas
- [ ] sem modelo ativo → fallback LAST_TOUCH
- [ ] publica `journey-os.receita.atribuida` com `versao_modelo`

## Dependencias
- SALE-004 (precede)

## Estimativa
L

## Prioridade
P2
