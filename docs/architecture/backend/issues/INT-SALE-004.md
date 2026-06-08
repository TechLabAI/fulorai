# INT-SALE-004 — Ingestão de compra do checkout/gateway (mediada)

## Contexto
Validar a ingestão idempotente de pedido confirmado vindo do checkout/gateway externo (Hotmart/link),
mediada por service token via GWY. INTL Event Platform é o caminho pós-MVP.

## Spec de referencia
- `contracts/integration-contracts.md` §2, `contracts/hub-integration.md` §3, SPEC-05

## Escopo
Teste de `POST /compras` com service token; idempotência por `(id_externo, origem)`; webhook
duplicado não recontabiliza receita. SALE não contata o gateway para cobrar.

## Resultado esperado
Fonte de compra desacoplada e segura a retries.

## Criterios de aceite
- [ ] ingestão exige service token (não anônimo)
- [ ] webhook duplicado → compra existente, sem nova receita
- [ ] SALE não executa pagamento (apenas registra confirmado)

## Dependencias
- SALE-004, SALE-013 (precede)

## Estimativa
M

## Prioridade
P4
