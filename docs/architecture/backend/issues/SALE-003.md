# SALE-003 — API CRUD de Oferta (catálogo versionado)

## Contexto
Expor `/api/v1/ofertas` (catálogo de produto+preço, versionado).

## Spec de referencia
- SPEC-01, `contracts/api-contract.md` §2, `contracts/data-model.md` §3.3

## Escopo
Controller + DTOs + `OfertaService` (create/findById/listAll/update/desativar). Edição cria nova
`versao`; versões anteriores imutáveis.

## Resultado esperado
Catálogo de ofertas gerenciável por API.

## Criterios de aceite
- [ ] editar oferta cria nova `versao` (anteriores imutáveis)
- [ ] `preco < 0` rejeitado com `sale.oferta.preco-invalido` (422)
- [ ] `desativar` marca `ativo=false`

## Dependencias
- SALE-001 (precede)

## Estimativa
S

## Prioridade
P1
