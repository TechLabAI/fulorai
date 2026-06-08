# WRKS-008 -- Migrations Flyway IAM (V0001..V0004 global) + seeds canônicos

## Contexto
DDL do IAM em `journeyos_global` e seeds dos papéis/permissões canônicos, materializados nas
migrations centralizadas (`journey-os-migrations`).

## Spec de referencia
- SPEC-04-data-model-migrations

## Escopo
- Extrair blocos ```sql``` de `contracts/data-model.md` (`-- schema: global`) para
  `db/migration/global/V0001__iam_papel_permissao.sql` .. `V0004__iam_auditoria.sql`
  (via `be-migration-generator.py`).
- Seeds: `papel` (INFOPRODUTOR/HEAD_GROWTH/SDR) + `permissao` (`wrks.*` + demais módulos) +
  bundles (`papel_permissao`) de `rbac.arch.json`/`permission-catalogue.arch.json`.
- `modelo_acesso_versao` inicializado em 1.

## Resultado esperado
Schema IAM criado e validável por `ddl-auto=validate`; seeds aplicados.

## Criterios de aceite
- [ ] Migrations aplicam limpo num banco vazio (Testcontainers).
- [ ] `empresa_id` rejeita slug fora de `^emp_[a-z0-9_]+$` (CHECK).
- [ ] Uniques (`usuario.email`, `papel.codigo`, `permissao.codigo`) ativos.
- [ ] Ordem V0001 (papel/permissao) antes de V0002 (associações, FK papel.codigo).

## Dependencias
- (precede WRKS-007); coordena com MIG (centralized Flyway)

## Estimativa
M

## Prioridade
P3
