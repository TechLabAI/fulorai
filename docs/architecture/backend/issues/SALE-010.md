# SALE-010 — Migrations Flyway (data-model → V__sale_*)

## Contexto
Gerar as migrations schema-aware do SALE a partir dos blocos SQL do `data-model.md`, no Flyway
centralizado (`journey-os-migrations`).

## Spec de referencia
- SPEC-04, `contracts/data-model.md` §5

## Escopo
`be-migration-generator.py` extrai os blocos `-- schema: empresa` → `db/migration/empresa/`.
Faixas: pipeline, catalog, purchases, attribution, ltv.

## Resultado esperado
Schema `emp_<slug>` preparado para o `validate` do serviço.

## Criterios de aceite
- [ ] migrations aplicam limpo a um `emp_<slug>` novo
- [ ] UNIQUE(`id_externo`,`origem`) e partial unique de `modelo_atribuicao` presentes
- [ ] faixas `V<N>` sem colisão (atribuídas por MIG)

## Dependencias
- SALE-009 (precede)

## Estimativa
M

## Prioridade
P3
