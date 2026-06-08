# SALE-004 — API de ingestão de Compra (idempotente)

## Contexto
Expor `POST /api/v1/compras` para ingestão idempotente de pedido confirmado por
`(id_externo, origem)`, além de listar/obter.

## Spec de referencia
- SPEC-01, SPEC-05, `contracts/api-contract.md` §3

## Escopo
Controller + DTOs + `CompraService.registrar` (idempotente) + findById/listAll. Reconhecimento de
receita + atribuição/LTV ficam em SALE-006/007/008 (orquestração).

## Resultado esperado
Endpoint de compra aceitando ingestão segura a retries.

## Criterios de aceite
- [ ] `POST /compras` com `(id_externo,origem)` novo cria compra (201)
- [ ] re-ingestão do mesmo `(id_externo,origem)` retorna existente (`duplicada=true`), sem nova receita
- [ ] Σ itens ≠ total → 422 `sale.compra.receita-inconsistente`
- [ ] `baseLegal` ausente/ inválida → 422 `sale.compra.base-legal-invalida`

## Dependencias
- SALE-001 (precede)

## Estimativa
M

## Prioridade
P1
