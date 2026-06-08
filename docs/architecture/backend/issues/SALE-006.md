# SALE-006 — Reconhecimento de receita na compra (golden path, âncora)

## Contexto
Orquestrar o golden path da âncora `compra.confirmada`: reconhecer receita (Σ itens = total),
encadear atribuição (SALE-007) e LTV (SALE-008) na mesma transação.

## Spec de referencia
- SPEC-02, `contracts/event-contracts.md` (`compra.confirmada`)

## Escopo
`CompraService.registrar` completo: cria `compra`+`item_compra`, valida conservação de receita,
dispara atribuição+LTV, publica `journey-os.compra.confirmada` via outbox.

## Resultado esperado
Compra confirmada gera receita reconhecida + eventos a jusante.

## Criterios de aceite
- [ ] `valor_total` = Σ `item_compra.valor_total` (invariante)
- [ ] publica `journey-os.compra.confirmada` no mesmo limite transacional (outbox)
- [ ] re-ingestão idempotente NÃO republica o evento
- [ ] venda direta (sem oportunidade) também reconhece receita

## Dependencias
- SALE-004 (precede), SALE-007, SALE-008

## Estimativa
L

## Prioridade
P2
