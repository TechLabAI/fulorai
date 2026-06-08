# ASST-007 -- Migrations Flyway (schema emp_<slug>)

## Contexto
DDL das tabelas de asset no schema operacional do tenant, gerado a partir de `data-model.md` e
roteado para a Flyway centralizada (MIG).

## Spec de referencia
- SPEC-04-data-model-migrations
- contracts/data-model.md

## Escopo
- Extrair os blocos `sql` de `data-model.md` (`-- schema: empresa`) → `db/migration/empresa/V<N>__asst_*.sql`.
- Tabelas `asset`, `versao_asset`, `aprovacao`, `tag_asset` (sem `empresa_id` — schema isola).
- Índices/constraints/CHECK conforme contrato; `gen_random_uuid()` (pgcrypto via MIG).
- Migração reside em `journey-os-migrations` (ASST roda `ddl-auto=validate`).

## Resultado esperado
Schema do tenant validável pelo Hibernate; nenhuma alteração de schema no boot do ASST.

## Criterios de aceite
- [ ] V<N> aplica as 4 tabelas no schema `emp_<slug>`.
- [ ] `(asset_id, numero)` UNIQUE em `versao_asset`.
- [ ] `ddl-auto=validate` passa contra o schema migrado.

## Dependencias
- ASST-002 (modelo); MIG (existente)

## Estimativa
M

## Prioridade
P3
