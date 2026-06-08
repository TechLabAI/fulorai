# SALE-009 — Persistência JPA + adapters (9 tabelas)

## Contexto
Implementar entidades JPA, repositories e adapters para as portas out de repositório das 9 tabelas
em `emp_<slug>`.

## Spec de referencia
- SPEC-04, `contracts/data-model.md`

## Escopo
`infrastructure.persistence` (entity/repository/adapter) para `oportunidade`, `historico_estagio`,
`oferta`, `compra`, `item_compra`, `modelo_atribuicao`, `atribuicao`, `campanha`, `ltv`.
`ddl-auto=validate`, `open-in-view=false`.

## Resultado esperado
Domínio persistido no schema do tenant.

## Criterios de aceite
- [ ] adapters implementam `*RepositoryPort` (api não depende de infra)
- [ ] valores monetários `NUMERIC(15,2)` + `moeda`
- [ ] `@Transactional` apenas em `application.service`
- [ ] boot com `ddl-auto=validate`

## Dependencias
- SALE-002, SALE-004 (precede)

## Estimativa
L

## Prioridade
P3
