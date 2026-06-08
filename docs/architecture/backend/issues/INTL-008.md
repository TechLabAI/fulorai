# INTL-008 -- Migration Flyway V1 (schema INTL)

## Contexto
Criar a migração inicial centralizada do schema de INTL.

## Spec de referência
- SPEC-04, `contracts/data-model.md`

## Escopo
`V1__intl_create_initial_schema.sql` (gerado por `be-migration-generator.py` dos blocos ```sql```
do data-model) com as 7 tabelas no schema `emp_<slug>`. Extensões `pgcrypto`/`vector` já criadas
pela V1 global do MIG (não duplicar). Migração vive em `journey-os-migrations`.

## Resultado esperado
Schema `emp_<slug>` preparado; `intl-service` valida em boot.

## Critérios de aceite
- [ ] 7 `CREATE TABLE` na ordem do data-model (FKs resolvidas)
- [ ] CHECKs de enum + UNIQUE (`conversa_id`,`ordem`) presentes
- [ ] Não recria extensões globais

## Dependências
- (data-model.md) — precede INTL-007

## Estimativa
M

## Prioridade
P3
